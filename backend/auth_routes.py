from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User, AuditLog
from security_utils import PasswordManager, RBACManager
from datetime import datetime
import uuid
import pyotp
import qrcode
from io import BytesIO
import base64

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def log_audit(user_id, action, resource_type, resource_id=None, details=None, ip_address=None):
    """Log audit trail"""
    # Some events (e.g., unknown-username login failures) have no user yet.
    # audit_logs.user_id is NOT NULL, so skip those inserts.
    if not user_id:
        return

    if not ip_address:
        ip_address = request.remote_addr
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    db.session.add(audit_log)
    db.session.commit()


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration with password policy validation"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Validate password policy
        is_valid, errors = PasswordManager.validate_password_policy(password)
        if not is_valid:
            return jsonify({'error': 'Password policy violation', 'details': errors}), 400
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=PasswordManager.hash_password(password),
            role='user'
        )
        
        db.session.add(user)
        db.session.commit()
        
        log_audit(user.id, 'USER_REGISTERED', 'user', user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with JWT token generation"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not PasswordManager.verify_password(password, user.password_hash):
            log_audit(None, 'LOGIN_FAILED', 'user', None, f'Failed login attempt for {username}')
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            # Generate temporary session token for 2FA verification
            temp_token = create_access_token(
                identity=user.id,
                expires_delta=None,
                additional_claims={'2fa_pending': True}
            )
            return jsonify({
                'message': '2FA verification required',
                'temp_token': temp_token,
                'requires_2fa': True
            }), 200
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        log_audit(user.id, 'LOGIN_SUCCESS', 'user')
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout"""
    try:
        user_id = get_jwt_identity()
        log_audit(user_id, 'LOGOUT', 'user')
        
        return jsonify({'message': 'Logout successful'}), 200
    
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500


@auth_bp.route('/2fa/setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    """Setup Two-Factor Authentication"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate secret
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR code
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='SecureDocumentVault'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.read()).decode()
        
        # Store secret temporarily (user needs to verify with token first)
        session['2fa_secret_temp'] = secret
        
        return jsonify({
            'message': '2FA setup initiated',
            'qr_code': qr_code_base64,
            'secret': secret,
            'manual_entry_key': secret
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'2FA setup failed: {str(e)}'}), 500


@auth_bp.route('/2fa/verify', methods=['POST'])
@jwt_required()
def verify_2fa():
    """Verify 2FA token and enable 2FA"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Missing 2FA token'}), 400
        
        secret = session.get('2fa_secret_temp')
        if not secret:
            return jsonify({'error': '2FA setup not initiated'}), 400
        
        totp = pyotp.TOTP(secret)
        if not totp.verify(token, valid_window=1):
            return jsonify({'error': 'Invalid 2FA token'}), 401
        
        # Enable 2FA
        user.two_factor_enabled = True
        user.two_factor_secret = secret
        db.session.commit()
        
        del session['2fa_secret_temp']
        
        log_audit(user_id, '2FA_ENABLED', 'user', user_id)
        
        return jsonify({'message': '2FA enabled successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'2FA verification failed: {str(e)}'}), 500


@auth_bp.route('/2fa/verify-login', methods=['POST'])
def verify_2fa_login():
    """Verify 2FA during login"""
    try:
        data = request.get_json()
        token = data.get('token')
        temp_token = data.get('temp_token')
        
        if not token or not temp_token:
            return jsonify({'error': 'Missing token or 2FA code'}), 400
        
        # Verify temp token
        from flask_jwt_extended import decode_token
        claims = decode_token(temp_token)
        
        if not claims.get('2fa_pending'):
            return jsonify({'error': 'Invalid request'}), 400
        
        user_id = claims.get('sub')
        user = User.query.get(user_id)
        
        if not user or not user.two_factor_enabled:
            return jsonify({'error': 'User not found or 2FA not enabled'}), 404
        
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(token, valid_window=1):
            log_audit(user_id, '2FA_VERIFICATION_FAILED', 'user')
            return jsonify({'error': 'Invalid 2FA token'}), 401
        
        # Generate actual tokens
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        log_audit(user_id, 'LOGIN_SUCCESS_2FA', 'user')
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'2FA verification failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'two_factor_enabled': user.two_factor_enabled,
                'created_at': user.created_at.isoformat()
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve user: {str(e)}'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Missing old or new password'}), 400
        
        # Verify old password
        if not PasswordManager.verify_password(old_password, user.password_hash):
            log_audit(user_id, 'PASSWORD_CHANGE_FAILED', 'user', user_id, 'Invalid old password')
            return jsonify({'error': 'Invalid old password'}), 401
        
        # Validate new password
        is_valid, errors = PasswordManager.validate_password_policy(new_password)
        if not is_valid:
            return jsonify({'error': 'Password policy violation', 'details': errors}), 400
        
        # Update password
        user.password_hash = PasswordManager.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(user_id, 'PASSWORD_CHANGED', 'user', user_id)
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500
