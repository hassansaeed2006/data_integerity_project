# Testing Checklist - Secure Document Vault

Use this checklist to verify all features are working correctly.

## 📋 Pre-Testing Setup

- [ ] Python 3.8+ installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Certificates generated: `python certificates/generate_certs.py`
- [ ] Backend running: `python backend/app.py`
- [ ] Server accessible: `https://localhost:5000`
- [ ] Browser accepts self-signed certificate

---

## 🔐 Authentication Tests

### User Registration

- [ ] Can access registration page
- [ ] Registration form displays all fields
- [ ] Form validates empty fields
- [ ] Password policy enforced:
  - [ ] Minimum 8 characters required
  - [ ] Uppercase letter required (A-Z)
  - [ ] Lowercase letter required (a-z)
  - [ ] Digit required (0-9)
  - [ ] Special character required (!@#$%^&*)
- [ ] Error shown for weak passwords
- [ ] Error shown for duplicate usernames
- [ ] Error shown for duplicate emails
- [ ] Successful registration shows success message
- [ ] Can login after registration
- [ ] Password never shown in plain text

### User Login

- [ ] Can access login page
- [ ] Login form displays username and password fields
- [ ] Error for empty username/password
- [ ] Error for non-existent username
- [ ] Error for incorrect password
- [ ] Successful login shows dashboard
- [ ] JWT token generated and stored
- [ ] Refresh token stored
- [ ] User information displayed correctly
- [ ] Can logout successfully

### Two-Factor Authentication (2FA)

#### Setup 2FA
- [ ] Can access Security Settings page
- [ ] 2FA setup button visible
- [ ] QR code displays after setup click
- [ ] Secret key displayed for manual entry
- [ ] QR code is scannable with authenticator apps:
  - [ ] Google Authenticator
  - [ ] Microsoft Authenticator
  - [ ] Authy
- [ ] Manual entry key works in authenticator
- [ ] Can submit 2FA verification code

#### Verify 2FA
- [ ] 2FA code validation works (6 digits)
- [ ] Invalid code rejected
- [ ] Valid code enables 2FA
- [ ] Success message shown after enabling
- [ ] 2FA status shows "Enabled"

#### 2FA Login
- [ ] Login with 2FA-enabled account shows 2FA prompt
- [ ] Temporary token issued for 2FA page
- [ ] 2FA code required before full login
- [ ] Invalid 2FA code rejects login
- [ ] Valid 2FA code completes login
- [ ] Full tokens issued after 2FA verification
- [ ] Audit log records 2FA verification

### Password Change

- [ ] Can access profile settings
- [ ] Password change form visible
- [ ] Current password validation works
- [ ] Wrong current password rejected
- [ ] New password policy enforced
- [ ] Password successfully changed
- [ ] Can login with new password
- [ ] Cannot login with old password
- [ ] Audit log records password change

### User Profile

- [ ] Can view own profile information
- [ ] Username displayed correctly
- [ ] Email displayed correctly
- [ ] Role displayed correctly
- [ ] 2FA status displayed correctly
- [ ] Creation date displayed
- [ ] Cannot edit other user profiles (non-admin)

---

## 📄 Document Management Tests

### Document Upload

- [ ] Can access Documents page
- [ ] Upload form displays file input
- [ ] File type validation works:
  - [ ] Accepts: PDF, DOC, DOCX, TXT, XLSX, CSV, PNG, JPG, JPEG
  - [ ] Rejects: EXE, COM, SH, BAT, etc.
- [ ] File size validation works:
  - [ ] Small files (< 500MB) accepted
  - [ ] Large files (> 500MB) rejected
- [ ] File upload shows progress
- [ ] Upload completion shows success message
- [ ] File appears in documents list
- [ ] Document metadata visible

### Encryption Verification

- [ ] Uploaded file stored encrypted (can't open directly from /uploads)
- [ ] File stored with random filename
- [ ] Encryption algorithm shown as AES-256
- [ ] Encryption salt generated and stored
- [ ] Document hash calculated (SHA-256)
- [ ] Document signature generated

### Document Listing

- [ ] Can see all own documents
- [ ] Document list shows:
  - [ ] Filename
  - [ ] File type
  - [ ] File size
  - [ ] Owner
  - [ ] Upload date/time
  - [ ] Verification status
- [ ] Managers can see all documents
- [ ] Admins can see all documents
- [ ] Regular users can only see own documents

### Document Details/Metadata

- [ ] Can click "Details" on document
- [ ] All metadata displays:
  - [ ] Original filename
  - [ ] File type
  - [ ] File size
  - [ ] Owner
  - [ ] Upload timestamp
  - [ ] SHA-256 hash
  - [ ] Digital signature (truncated)
  - [ ] Encryption algorithm
  - [ ] Description (if provided)
- [ ] Metadata is read-only

### Document Download

- [ ] Can download own documents
- [ ] Downloaded file automatically decrypted
- [ ] Downloaded file has original filename
- [ ] Downloaded file content is correct
- [ ] File opens and displays correctly
- [ ] Large files download completely
- [ ] Download logged in audit trail

### Document Verification

- [ ] Can verify own documents
- [ ] Verification checks:
  - [ ] SHA-256 hash comparison
  - [ ] Digital signature verification
  - [ ] Both checks pass for unmodified files
- [ ] Verification shows:
  - [ ] Original hash
  - [ ] Current hash
  - [ ] Hash match status
  - [ ] Signature validation status
  - [ ] Overall verification status
- [ ] Unmodified file shows "VERIFIED"
- [ ] Tampered file shows "TAMPERED"
- [ ] Verification logged in audit trail

### Document Deletion

- [ ] Can delete own documents
- [ ] Delete confirmation required
- [ ] Document removed from list
- [ ] File deleted from storage
- [ ] Database record deleted
- [ ] Deletion logged in audit trail
- [ ] Admin can delete any document

---

## 👥 Role-Based Access Control Tests

### User Role

**Permissions**: Upload, download, manage own documents, verify own documents

- [ ] Can upload documents
- [ ] Can download own documents
- [ ] Can verify own documents
- [ ] Can delete own documents
- [ ] Cannot access admin panel
- [ ] Cannot manage other users
- [ ] Cannot see other users' documents
- [ ] Cannot access manager features

### Manager Role

**Permissions**: Upload, review documents, verify documents

- [ ] Can upload documents
- [ ] Can see all documents
- [ ] Can review documents
- [ ] Can verify documents
- [ ] Cannot access admin panel
- [ ] Cannot manage users
- [ ] Cannot change user roles

### Admin Role

**Permissions**: Full access to system

- [ ] Can access admin panel
- [ ] Can view all users
- [ ] Can change user roles
- [ ] Can activate/deactivate users
- [ ] Can delete users
- [ ] Can view audit logs
- [ ] Can view system statistics
- [ ] Can see all documents
- [ ] Can delete any document
- [ ] Cannot delete own account

---

## 🛡️ Admin Panel Tests

### Statistics Dashboard

- [ ] Statistics page displays:
  - [ ] Total users
  - [ ] Active users
  - [ ] User count by role
  - [ ] Total documents
  - [ ] Encrypted documents
  - [ ] Verified documents
  - [ ] Audit log entries
- [ ] Numbers update correctly
- [ ] Statistics are read-only

### User Management

- [ ] Can view list of all users
- [ ] User list shows:
  - [ ] Username
  - [ ] Email
  - [ ] Current role
  - [ ] Status (active/inactive)
  - [ ] 2FA status
  - [ ] Last login
- [ ] Can change user roles:
  - [ ] User → Manager
  - [ ] Manager → Admin
  - [ ] Admin → User
  - [ ] Change confirmed in database
- [ ] Can activate users
- [ ] Can deactivate users
- [ ] Can delete users (except self)
- [ ] Delete confirmation required
- [ ] User actions logged in audit trail

### Audit Logs

- [ ] Can view audit logs
- [ ] Audit logs show:
  - [ ] Action performed
  - [ ] Resource type
  - [ ] User who performed action
  - [ ] Timestamp
  - [ ] IP address
  - [ ] Action details
- [ ] Logs are in chronological order (newest first)
- [ ] Can scroll through many logs
- [ ] Logs persist between sessions

---

## 🔒 Security Tests

### Password Security

- [ ] Passwords hashed (not readable in database)
- [ ] Same password shows different hash (salt)
- [ ] Cannot login with old password hash
- [ ] Password change invalidates old password

### Encryption

- [ ] Files encrypted in storage
- [ ] Uploaded files cannot be read directly
- [ ] Encryption uses AES-256
- [ ] Different files have different encryption salts
- [ ] Decryption works only with correct user credentials

### Digital Signatures

- [ ] Every document has signature
- [ ] Signature algorithm shown (SHA-256)
- [ ] Signature validates for unmodified files
- [ ] Signature fails if file modified
- [ ] Signature stored persistently

### Integrity Verification

- [ ] SHA-256 hash calculated for every file
- [ ] Hashes are 64-character hex strings
- [ ] Hash remains constant for same file
- [ ] Modification detection works (hash changes)
- [ ] Hashes stored persistently

### HTTPS/TLS

- [ ] Application accessible only on HTTPS
- [ ] HTTP redirects to HTTPS (or not accessible)
- [ ] Certificate present (self-signed for dev)
- [ ] All communication encrypted
- [ ] Certificate valid for localhost

### Audit Logging

- [ ] Login events logged
- [ ] Logout events logged
- [ ] File upload logged
- [ ] File download logged
- [ ] File deletion logged
- [ ] File verification logged
- [ ] User role changes logged
- [ ] User status changes logged
- [ ] Failed authentication attempts logged
- [ ] IP addresses recorded
- [ ] Timestamps accurate

---

## 🌐 User Interface Tests

### Navigation

- [ ] Navigation bar displays correctly
- [ ] All navigation links work
- [ ] Active page highlighted
- [ ] Can navigate between pages
- [ ] User menu shows when authenticated
- [ ] User menu hidden when not authenticated

### Responsive Design

- [ ] Works on desktop (1920x1080)
- [ ] Works on tablet (1024x768)
- [ ] Works on mobile (375x667)
- [ ] Forms display correctly on all sizes
- [ ] Navigation adapts to screen size
- [ ] Documents list readable on mobile
- [ ] Buttons clickable on mobile

### Forms & Validation

- [ ] All form inputs display correctly
- [ ] Form labels clear and visible
- [ ] Placeholders helpful
- [ ] Required field indicators clear
- [ ] Error messages descriptive
- [ ] Success messages clear
- [ ] Form data cleared after submission

### Accessibility

- [ ] Page titles descriptive
- [ ] Links have title text
- [ ] Buttons have clear labels
- [ ] Color not only means (also text/icons)
- [ ] Can use keyboard navigation (Tab key)
- [ ] Form inputs accessible with keyboard

---

## 🔄 Integration Tests

### Authentication → Document Management

- [ ] Login → Access documents
- [ ] Logout → Cannot access protected pages
- [ ] New user → Can upload immediately
- [ ] Session expires → Require re-login

### Document Upload → Verification

- [ ] Upload file → Can download immediately
- [ ] Download file → Content correct
- [ ] Verify file → Shows hash and signature
- [ ] Unmodified file → Verification passes

### Role Changes → Access

- [ ] User → Manager → Can verify documents
- [ ] Manager → Admin → Can access admin panel
- [ ] Admin → User → Cannot access admin panel

### 2FA → Login

- [ ] Enable 2FA → Required at next login
- [ ] 2FA code required → Cannot skip
- [ ] Valid code → Full login
- [ ] Invalid code → Login fails

---

## ⚠️ Error Handling Tests

### Invalid Input

- [ ] Empty username error handled
- [ ] Empty password error handled
- [ ] Invalid email format error handled
- [ ] File too large error handled
- [ ] Invalid file type error handled
- [ ] Missing required fields error handled

### Business Logic Errors

- [ ] Duplicate username rejected
- [ ] Duplicate email rejected
- [ ] Duplicate file detected
- [ ] Modification detected (hash mismatch)
- [ ] Permission denied shown properly
- [ ] Resource not found handled

### System Errors

- [ ] Database errors handled gracefully
- [ ] File system errors handled
- [ ] Network errors handled
- [ ] Server errors handled
- [ ] Error messages don't expose system info

---

## 📊 Performance Tests

- [ ] Page loads within 3 seconds
- [ ] Large document list loads smoothly
- [ ] File upload progress visible
- [ ] File download completes without timeout
- [ ] Admin statistics page loads quickly
- [ ] Audit logs load with pagination

---

## 🔗 API Tests

### Authentication Endpoints

- [ ] POST /api/auth/register - Returns 201 on success
- [ ] POST /api/auth/login - Returns JWT tokens
- [ ] POST /api/auth/refresh - Refreshes access token
- [ ] POST /api/auth/logout - Clears session
- [ ] GET /api/auth/me - Returns current user
- [ ] POST /api/auth/change-password - Updates password

### Document Endpoints

- [ ] POST /api/documents/upload - Encrypts and stores
- [ ] GET /api/documents - Lists documents
- [ ] GET /api/documents/<id>/metadata - Returns details
- [ ] GET /api/documents/<id>/download - Decrypts file
- [ ] GET /api/documents/<id>/verify - Verifies integrity
- [ ] DELETE /api/documents/<id> - Removes document

### Admin Endpoints

- [ ] GET /api/admin/users - Lists all users
- [ ] PUT /api/admin/users/<id>/role - Updates role
- [ ] PUT /api/admin/users/<id>/status - Updates status
- [ ] DELETE /api/admin/users/<id> - Deletes user
- [ ] GET /api/admin/audit-logs - Returns audit logs
- [ ] GET /api/admin/statistics - Returns statistics

---

## 📝 Cross-Browser Testing

### Chrome
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

### Firefox
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

### Safari
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

### Edge
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

---

## ✅ Final Sign-Off

- [ ] All critical features tested
- [ ] No blocking issues
- [ ] Security features verified
- [ ] Documentation complete
- [ ] README updated
- [ ] Project ready for submission

**Tested by:** _________________

**Date:** _________________

**Overall Status:** ⬜ Pass / ⬜ Fail

**Issues Found:** (attach separate list if needed)

---

**Note:** This is a comprehensive checklist. Not all items may be applicable to your deployment. Use your judgment and focus on critical features for your deadline.
