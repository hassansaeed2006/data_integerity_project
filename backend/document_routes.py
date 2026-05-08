from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Document, User, AuditLog
from security_utils import (
    EncryptionManager, IntegrityManager, RBACManager, validate_file_upload
)
from werkzeug.utils import secure_filename
from config import Config
import os
import uuid
from datetime import datetime

doc_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

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


@doc_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload and encrypt document"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not RBACManager.has_permission(user.role, 'upload_documents'):
            log_audit(user_id, 'UPLOAD_DENIED', 'document', None, 'Permission denied')
            return jsonify({'error': 'Permission denied'}), 403
        
        # Check for file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        is_valid, error = validate_file_upload(file.filename, len(file.getvalue()))
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Read file content
        file_content = file.read()
        
        # Calculate hash before encryption
        file_hash = IntegrityManager.calculate_sha256(file_content)
        
        # Check if file already exists (duplicate)
        if Document.query.filter_by(sha256_hash=file_hash).first():
            return jsonify({'error': 'File with same content already exists'}), 409
        
        # Encrypt file
        encryption_key = user_id[:32]  # Use user ID as basis for encryption key
        encrypted_content, salt = EncryptionManager.encrypt_file(file_content, encryption_key)
        
        # Generate digital signature
        digital_signature = IntegrityManager.generate_signature(
            file_content,
            encryption_key.encode()[:32]
        )
        
        # Create document record
        stored_filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_type = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
        
        document = Document(
            id=str(uuid.uuid4()),
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size=len(file_content),
            encrypted=True,
            encryption_algorithm='AES-256',
            encryption_key_salt=salt,
            sha256_hash=file_hash,
            digital_signature=digital_signature,
            signature_algorithm='SHA-256',
            description=request.form.get('description', ''),
            is_verified=True,
            is_modified=False
        )
        
        # Save encrypted file
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        with open(os.path.join(Config.UPLOAD_FOLDER, stored_filename), 'wb') as f:
            f.write(encrypted_content)
        
        db.session.add(document)
        db.session.commit()
        
        log_audit(user_id, 'DOCUMENT_UPLOADED', 'document', document.id, f'File: {file.filename}')
        
        return jsonify({
            'message': 'Document uploaded and encrypted successfully',
            'document': {
                'id': document.id,
                'filename': document.original_filename,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'sha256_hash': document.sha256_hash,
                'created_at': document.created_at.isoformat(),
                'encrypted': document.encrypted
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Document upload failed: {str(e)}'}), 500


@doc_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """List user's documents"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Different rules for different roles
        if RBACManager.is_admin(user.role):
            # Admin can see all documents
            documents = Document.query.all()
        elif RBACManager.is_manager(user.role):
            # Manager can see all documents
            documents = Document.query.all()
        else:
            # Users can only see their own documents
            documents = Document.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'documents': [{
                'id': doc.id,
                'filename': doc.original_filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'sha256_hash': doc.sha256_hash,
                'owner_id': doc.user_id,
                'owner': doc.owner.username,
                'created_at': doc.created_at.isoformat(),
                'is_verified': doc.is_verified,
                'is_modified': doc.is_modified,
                'encrypted': doc.encrypted
            } for doc in documents]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve documents: {str(e)}'}), 500


@doc_bp.route('/<doc_id>/metadata', methods=['GET'])
@jwt_required()
def get_document_metadata(doc_id):
    """Get document metadata"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        document = Document.query.get(doc_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check access
        if document.user_id != user_id and not RBACManager.is_manager(user.role):
            return jsonify({'error': 'Access denied'}), 403
        
        log_audit(user_id, 'DOCUMENT_VIEWED', 'document', doc_id)
        
        return jsonify({
            'document': {
                'id': document.id,
                'filename': document.original_filename,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'owner': document.owner.username,
                'owner_id': document.user_id,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat(),
                'sha256_hash': document.sha256_hash,
                'signature_algorithm': document.signature_algorithm,
                'digital_signature': document.digital_signature[:50] + '...' if document.digital_signature else None,
                'is_verified': document.is_verified,
                'is_modified': document.is_modified,
                'encrypted': document.encrypted,
                'encryption_algorithm': document.encryption_algorithm,
                'description': document.description
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve metadata: {str(e)}'}), 500


@doc_bp.route('/<doc_id>/download', methods=['GET'])
@jwt_required()
def download_document(doc_id):
    """Download and decrypt document"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        document = Document.query.get(doc_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check access
        if document.user_id != user_id and not RBACManager.has_permission(user.role, 'download_documents'):
            log_audit(user_id, 'DOWNLOAD_DENIED', 'document', doc_id, 'Permission denied')
            return jsonify({'error': 'Access denied'}), 403
        
        # Read encrypted file
        file_path = os.path.join(Config.UPLOAD_FOLDER, document.stored_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Decrypt with the document owner's key (not the current viewer's key).
        encryption_key = document.user_id[:32]
        try:
            decrypted_content = EncryptionManager.decrypt_file(
                encrypted_content,
                encryption_key,
                document.encryption_key_salt
            )
        except ValueError as e:
            # Encrypted blob was altered/corrupted; mark document as tampered.
            document.is_modified = True
            document.is_verified = False
            db.session.commit()
            log_audit(user_id, 'INTEGRITY_CHECK_FAILED', 'document', doc_id, f'Decryption failed: {str(e)}')
            return jsonify({'error': 'Integrity verification failed - encrypted file is corrupted or modified'}), 409
        
        # Verify integrity
        current_hash = IntegrityManager.calculate_sha256(decrypted_content)
        if current_hash != document.sha256_hash:
            document.is_modified = True
            document.is_verified = False
            db.session.commit()
            log_audit(user_id, 'INTEGRITY_CHECK_FAILED', 'document', doc_id, 'File hash mismatch')
            return jsonify({'error': 'Integrity verification failed - file may have been modified'}), 409
        
        log_audit(user_id, 'DOCUMENT_DOWNLOADED', 'document', doc_id)
        
        return send_file(
            BytesIO(decrypted_content),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=document.original_filename
        )
    
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@doc_bp.route('/<doc_id>/verify', methods=['GET'])
@jwt_required()
def verify_document(doc_id):
    """Verify document integrity and signature"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        document = Document.query.get(doc_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check access
        if document.user_id != user_id and not RBACManager.is_manager(user.role):
            return jsonify({'error': 'Access denied'}), 403
        
        # Read encrypted file
        file_path = os.path.join(Config.UPLOAD_FOLDER, document.stored_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Decrypt with the document owner's key (not the current verifier's key).
        encryption_key = document.user_id[:32]
        try:
            decrypted_content = EncryptionManager.decrypt_file(
                encrypted_content,
                encryption_key,
                document.encryption_key_salt
            )
        except ValueError as e:
            # Decryption failure indicates tampering/corruption of encrypted data.
            document.is_modified = True
            document.is_verified = False
            db.session.commit()
            log_audit(user_id, 'DOCUMENT_VERIFIED', 'document', doc_id,
                     f'Hash valid: False, Signature valid: False, Decryption failed: {str(e)}')
            return jsonify({
                'verification': {
                    'document_id': document.id,
                    'filename': document.original_filename,
                    'integrity_check': {
                        'valid': False,
                        'original_hash': document.sha256_hash,
                        'current_hash': None
                    },
                    'signature_check': {
                        'valid': False,
                        'algorithm': document.signature_algorithm,
                        'signature': document.digital_signature[:50] + '...' if document.digital_signature else None
                    },
                    'overall_status': 'TAMPERED',
                    'verified_at': datetime.utcnow().isoformat(),
                    'error': 'Encrypted file is corrupted or modified'
                }
            }), 200
        
        # Verify hash
        current_hash = IntegrityManager.calculate_sha256(decrypted_content)
        hash_valid = current_hash == document.sha256_hash
        
        # Verify signature
        encryption_key_bytes = document.user_id[:32].encode()[:32]
        signature_valid = IntegrityManager.verify_signature(
            decrypted_content,
            document.digital_signature,
            encryption_key_bytes
        )
        
        # Update verification status
        document.is_modified = not (hash_valid and signature_valid)
        document.is_verified = hash_valid and signature_valid
        db.session.commit()
        
        log_audit(user_id, 'DOCUMENT_VERIFIED', 'document', doc_id, 
                 f'Hash valid: {hash_valid}, Signature valid: {signature_valid}')
        
        return jsonify({
            'verification': {
                'document_id': document.id,
                'filename': document.original_filename,
                'integrity_check': {
                    'valid': hash_valid,
                    'original_hash': document.sha256_hash,
                    'current_hash': current_hash
                },
                'signature_check': {
                    'valid': signature_valid,
                    'algorithm': document.signature_algorithm,
                    'signature': document.digital_signature[:50] + '...'
                },
                'overall_status': 'VERIFIED' if (hash_valid and signature_valid) else 'TAMPERED',
                'verified_at': datetime.utcnow().isoformat()
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500


@doc_bp.route('/<doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete document"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        document = Document.query.get(doc_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check access
        if document.user_id != user_id and not RBACManager.is_admin(user.role):
            log_audit(user_id, 'DELETE_DENIED', 'document', doc_id, 'Permission denied')
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete file
        file_path = os.path.join(Config.UPLOAD_FOLDER, document.stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        log_audit(user_id, 'DOCUMENT_DELETED', 'document', doc_id)
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500


from io import BytesIO
