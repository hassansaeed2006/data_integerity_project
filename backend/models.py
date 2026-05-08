from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # admin, manager, user
    
    # 2FA
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(255), nullable=True)
    
    # OAuth
    github_id = db.Column(db.String(50), unique=True, nullable=True)
    google_id = db.Column(db.String(50), unique=True, nullable=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    
    # Encryption
    encrypted = db.Column(db.Boolean, default=True)
    encryption_algorithm = db.Column(db.String(50), default='AES-256')
    encryption_key_salt = db.Column(db.String(255), nullable=True)
    
    # Integrity & Signature
    sha256_hash = db.Column(db.String(64), nullable=False, unique=True)  # SHA-256 hash
    digital_signature = db.Column(db.Text, nullable=True)
    signature_algorithm = db.Column(db.String(50), default='SHA-256')
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, default=True)
    is_modified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # document, user, system
    resource_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'


class VerificationToken(db.Model):
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    token_type = db.Column(db.String(50), nullable=False)  # email_verification, password_reset
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VerificationToken {self.token_type}>'
