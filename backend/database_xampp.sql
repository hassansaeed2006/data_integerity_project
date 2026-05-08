-- Secure Document Vault - MySQL schema for XAMPP
-- Run this script in phpMyAdmin or MySQL CLI.

CREATE DATABASE IF NOT EXISTS secure_document_vault
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE secure_document_vault;

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) NOT NULL,
  username VARCHAR(80) NOT NULL,
  email VARCHAR(120) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  two_factor_enabled TINYINT(1) DEFAULT 0,
  two_factor_secret VARCHAR(255) DEFAULT NULL,
  github_id VARCHAR(50) DEFAULT NULL,
  google_id VARCHAR(50) DEFAULT NULL,
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME DEFAULT NULL,
  password_changed_at DATETIME DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username),
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_github_id (github_id),
  UNIQUE KEY uq_users_google_id (google_id),
  KEY ix_users_username (username),
  KEY ix_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS documents (
  id VARCHAR(36) NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  stored_filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(50) NOT NULL,
  file_size INT NOT NULL,
  encrypted TINYINT(1) DEFAULT 1,
  encryption_algorithm VARCHAR(50) DEFAULT 'AES-256',
  encryption_key_salt VARCHAR(255) DEFAULT NULL,
  sha256_hash VARCHAR(64) NOT NULL,
  digital_signature TEXT,
  signature_algorithm VARCHAR(50) DEFAULT 'SHA-256',
  description TEXT,
  is_verified TINYINT(1) DEFAULT 1,
  is_modified TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_public TINYINT(1) DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_documents_stored_filename (stored_filename),
  UNIQUE KEY uq_documents_sha256_hash (sha256_hash),
  KEY ix_documents_user_id (user_id),
  KEY ix_documents_created_at (created_at),
  CONSTRAINT fk_documents_user_id
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_logs (
  id VARCHAR(36) NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  action VARCHAR(255) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id VARCHAR(36) DEFAULT NULL,
  details TEXT,
  ip_address VARCHAR(45) DEFAULT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_audit_logs_user_id (user_id),
  KEY ix_audit_logs_timestamp (timestamp),
  CONSTRAINT fk_audit_logs_user_id
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS verification_tokens (
  id VARCHAR(36) NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  token VARCHAR(255) NOT NULL,
  token_type VARCHAR(50) NOT NULL,
  expires_at DATETIME NOT NULL,
  used TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_verification_tokens_token (token),
  KEY ix_verification_tokens_user_id (user_id),
  CONSTRAINT fk_verification_tokens_user_id
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
