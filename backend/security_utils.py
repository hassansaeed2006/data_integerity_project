import bcrypt
import os
import hashlib
import hmac
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import re
from config import Config

class PasswordManager:
    """Handles password hashing, verification, and policy enforcement"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def validate_password_policy(password):
        """
        Validate password against security policy
        Returns: (is_valid, error_message)
        """
        errors = []
        
        # Minimum length
        if len(password) < Config.MIN_PASSWORD_LENGTH:
            errors.append(f'Password must be at least {Config.MIN_PASSWORD_LENGTH} characters long')
        
        # Uppercase
        if Config.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        
        # Lowercase
        if Config.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        
        # Digits
        if Config.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append('Password must contain at least one digit')
        
        # Special characters
        if Config.REQUIRE_SPECIAL_CHARS:
            special_char_pattern = '[' + re.escape(Config.SPECIAL_CHARS) + ']'
            if not re.search(special_char_pattern, password):
                errors.append(f'Password must contain at least one special character: {Config.SPECIAL_CHARS}')
        
        return (len(errors) == 0, errors)


class EncryptionManager:
    """Handles document encryption and decryption using AES-256"""
    
    @staticmethod
    def derive_key(password, salt):
        """Derive encryption key from password using PBKDF2"""
        if isinstance(salt, str):
            salt = salt.encode()
        
        # Use hashlib's PBKDF2-HMAC-SHA256 for key derivation
        key_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000,
            dklen=32
        )
        key = urlsafe_b64encode(key_bytes)
        return key
    
    @staticmethod
    def encrypt_file(file_content, password):
        """
        Encrypt file content using Fernet (AES-128 in CBC mode)
        Returns: (encrypted_content, salt)
        """
        salt = os.urandom(16)
        key = EncryptionManager.derive_key(password, salt)
        cipher = Fernet(key)
        encrypted_content = cipher.encrypt(file_content)
        return encrypted_content, urlsafe_b64encode(salt).decode()
    
    @staticmethod
    def decrypt_file(encrypted_content, password, salt):
        """Decrypt file content"""
        try:
            key = EncryptionManager.derive_key(password, urlsafe_b64decode(salt.encode()))
            cipher = Fernet(key)
            decrypted_content = cipher.decrypt(encrypted_content)
            return decrypted_content
        except Exception as e:
            raise ValueError(f'Decryption failed: {str(e)}')


class IntegrityManager:
    """Handles document integrity verification and digital signatures"""
    
    @staticmethod
    def calculate_sha256(file_content):
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def generate_signature(file_content, private_key_bytes):
        """
        Generate HMAC-SHA256 signature for file content
        In production, use proper asymmetric cryptography (RSA/ECDSA)
        """
        signature = hmac.new(
            private_key_bytes,
            file_content,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(file_content, signature, private_key_bytes):
        """Verify file signature"""
        expected_signature = IntegrityManager.generate_signature(file_content, private_key_bytes)
        return hmac.compare_digest(signature, expected_signature)


class RBACManager:
    """Role-Based Access Control"""
    
    ROLES = {
        'admin': ['manage_users', 'manage_roles', 'review_documents', 'delete_documents', 'upload_documents', 'verify_documents', 'view_audit_logs', 'download_documents'],
        'manager': ['review_documents', 'verify_documents', 'upload_documents', 'delete_documents', 'download_documents'],
        'user': ['upload_documents', 'download_documents', 'view_own_documents', 'delete_own_documents', 'verify_own_documents']
    }
    
    @staticmethod
    def has_permission(user_role, permission):
        """Check if user role has permission"""
        if user_role not in RBACManager.ROLES:
            return False
        return permission in RBACManager.ROLES[user_role]
    
    @staticmethod
    def get_permissions(user_role):
        """Get all permissions for a role"""
        return RBACManager.ROLES.get(user_role, [])
    
    @staticmethod
    def is_admin(user_role):
        """Check if user is admin"""
        return user_role == 'admin'
    
    @staticmethod
    def is_manager(user_role):
        """Check if user is manager or admin"""
        return user_role in ['admin', 'manager']


def validate_file_upload(filename, file_size):
    """
    Validate file upload
    Returns: (is_valid, error_message)
    """
    # Check file size
    if file_size > Config.MAX_CONTENT_LENGTH:
        return False, f'File size exceeds maximum allowed size ({Config.MAX_CONTENT_LENGTH / 1024 / 1024}MB)'
    
    # Check file extension
    if '.' not in filename:
        return False, 'File must have an extension'
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        return False, f'File type .{file_ext} is not allowed. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
    
    return True, None
