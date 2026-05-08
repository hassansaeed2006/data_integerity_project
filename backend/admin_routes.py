from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, AuditLog
from security_utils import RBACManager
from datetime import datetime
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def log_audit(user_id, action, resource_type, resource_id=None, details=None, ip_address=None):
    """Log audit trail"""
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


@admin_bp.before_request
@jwt_required()
def check_admin_role():
    """Check if user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not RBACManager.is_admin(user.role):
        log_audit(user_id, 'ADMIN_ACCESS_DENIED', 'user', user_id)
        return jsonify({'error': 'Admin access required'}), 403


@admin_bp.route('/users', methods=['GET'])
def list_users():
    """List all users"""
    try:
        users = User.query.all()
        
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'two_factor_enabled': user.two_factor_enabled,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            } for user in users]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve users: {str(e)}'}), 500


@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """Update user role"""
    try:
        admin_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['admin', 'manager', 'user']:
            return jsonify({'error': 'Invalid role'}), 400
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        log_audit(admin_id, 'USER_ROLE_CHANGED', 'user', user_id, f'Role changed from {old_role} to {new_role}')
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Role update failed: {str(e)}'}), 500


@admin_bp.route('/users/<user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    """Activate or deactivate user"""
    try:
        admin_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'Missing is_active field'}), 400
        
        user.is_active = is_active
        db.session.commit()
        
        status = 'activated' if is_active else 'deactivated'
        log_audit(admin_id, 'USER_STATUS_CHANGED', 'user', user_id, f'User {status}')
        
        return jsonify({
            'message': f'User {status} successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_active': user.is_active
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Status update failed: {str(e)}'}), 500


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user and associated data"""
    try:
        admin_id = get_jwt_identity()
        
        # Prevent admin from deleting themselves
        if user_id == admin_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        log_audit(admin_id, 'USER_DELETED', 'user', user_id, f'User {username} deleted')
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User deletion failed: {str(e)}'}), 500


@admin_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()
        total = AuditLog.query.count()
        
        return jsonify({
            'logs': [{
                'id': log.id,
                'user_id': log.user_id,
                'username': log.user.username if log.user else 'Unknown',
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'details': log.details,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat()
            } for log in logs],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve audit logs: {str(e)}'}), 500


@admin_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_admins = User.query.filter_by(role='admin').count()
        total_managers = User.query.filter_by(role='manager').count()
        total_regular_users = User.query.filter_by(role='user').count()
        
        # Import Document here to avoid circular imports
        from models import Document
        total_documents = Document.query.count()
        encrypted_documents = Document.query.filter_by(encrypted=True).count()
        verified_documents = Document.query.filter_by(is_verified=True).count()
        
        total_audit_logs = AuditLog.query.count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'user_roles': {
                'admins': total_admins,
                'managers': total_managers,
                'regular_users': total_regular_users
            },
            'documents': {
                'total': total_documents,
                'encrypted': encrypted_documents,
                'verified': verified_documents
            },
            'audit_logs': total_audit_logs
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve statistics: {str(e)}'}), 500
