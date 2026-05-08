# Secure Document Vault System

A modern, enterprise-grade web application for secure document management with end-to-end encryption, digital signatures, multi-factor authentication, and role-based access control.

## 🔒 Security Features

### Authentication & Access Control
- ✅ User registration and login with password hashing (bcrypt, 12 rounds)
- ✅ JWT-based authentication with refresh tokens
- ✅ Two-Factor Authentication (2FA) using TOTP
- ✅ Password policy enforcement (8+ chars, uppercase, lowercase, digit, special char)
- ✅ OAuth login integration (GitHub/Google ready)
- ✅ Role-Based Access Control (RBAC) - Admin, Manager, User

### Encryption & Integrity
- ✅ AES-256 end-to-end document encryption
- ✅ SHA-256 document hashing for integrity verification
- ✅ HMAC-SHA256 digital signatures
- ✅ Document tampering detection
- ✅ Audit logging of all operations

### Security Communication
- ✅ HTTPS with self-signed certificates (development)
- ✅ CORS security headers
- ✅ Secure file uploads with type validation
- ✅ IP address logging for audit trails

## 📋 System Requirements

### Backend
- Python 3.8+
- Flask 2.3+
- SQLite 3
- OpenSSL (for certificate generation)

### Frontend
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- HTTPS support

## 🚀 Installation & Setup

### 1. Clone and Navigate to Project
```bash
cd d:\UNI\lvl 3\sem2\data\project
```

### 2. Install Python Dependencies

Install requirements in the backend folder:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Generate HTTPS Certificates

Navigate to the certificates folder and run:
```bash
cd certificates
python generate_certs.py
```

If you access the app using a LAN IP (example: `https://192.168.x.x:5000`), regenerate the cert with:
```bash
python generate_certs.py --force
```
This includes detected local IP addresses in certificate SAN fields.

This will create:
- `cert.pem` - Self-signed certificate
- `key.pem` - Private key

**Note**: Your browser will show a security warning. Click "Advanced" → "Proceed" to continue. This is normal for self-signed certificates.
To remove the warning entirely, import/trust `certificates/cert.pem` in your OS/browser certificate trust store.

### 4. Initialize Database

The database is automatically created when you first run the application.

```bash
cd backend
python app.py
```

### 5. Create Environment Variables (Optional)

Create a `.env` file in the backend folder:
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
GITHUB_CLIENT_ID=your-github-id
GITHUB_CLIENT_SECRET=your-github-secret
GOOGLE_CLIENT_ID=your-google-id
GOOGLE_CLIENT_SECRET=your-google-secret
```

## 🏃 Running the Application

### Start the Backend Server

From the `backend` folder:
```bash
python app.py
```

The server will start at: `https://localhost:5000`

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on https://localhost:5000
```

### Access the Application

Open your browser and navigate to:
```
https://localhost:5000
```

**Important**: 
1. You may see a security warning - this is expected with self-signed certificates
2. Click "Advanced" and then "Proceed" or "Continue" to access the application
3. The warning will not appear in subsequent visits

## 👥 Default Test Accounts

After first run, create test accounts through the registration page.

### Creating Test Users

1. **Admin User**
   - Username: `admin`
   - Email: `admin@vault.local`
   - Password: `SecurePass123!`

2. **Manager User**
   - Username: `manager`
   - Email: `manager@vault.local`
   - Password: `SecurePass123!`

3. **Regular User**
   - Username: `user`
   - Email: `user@vault.local`
   - Password: `SecurePass123!`

## 📱 Application Features

### 1. Authentication
- **Registration**: Create account with password policy validation
- **Login**: Username/password authentication
- **2FA Setup**: Enable TOTP-based two-factor authentication
- **Profile**: View and update user profile
- **Password Change**: Secure password change with validation

### 2. Document Management
- **Upload**: Upload documents up to 500MB
- **Encryption**: Automatic AES-256 encryption
- **Download**: Automatic decryption on download
- **Verification**: Check document integrity and signatures
- **Metadata**: View document details, hashes, and signatures
- **Delete**: Secure document deletion

### 3. Roles & Permissions

#### Admin
- Manage users and roles
- View all documents
- View audit logs
- Access admin panel
- Verify all documents

#### Manager
- Upload and delete documents
- Review and verify documents
- View own documents

#### User
- Upload and manage own documents
- Download own documents
- Verify own documents
- Delete own documents

### 4. Admin Panel
- **Statistics**: System overview (users, documents, audit logs)
- **User Management**: Create, edit, activate/deactivate users
- **Role Assignment**: Change user roles
- **Audit Logs**: View system activity logs

## 🔐 Security Concepts Demonstrated

### 1. Password Security
- **Bcrypt Hashing**: Passwords hashed with 12 salt rounds
- **Password Policy**: Requirements enforced at registration and password change
- **Salt Rotation**: Each password has unique salt
- Never stored in plain text

### 2. Encryption
- **AES-256**: Industry standard for document encryption
- **PBKDF2**: Key derivation from user ID
- **Per-Document Salt**: Each file has unique encryption salt
- **No Key Storage**: Keys derived from user ID on demand

### 3. Digital Signatures
- **HMAC-SHA256**: Sign documents for authenticity
- **Integrity Verification**: Detect any file modifications
- **Hash Comparison**: Compare original vs current hash

### 4. Authentication
- **JWT Tokens**: Stateless authentication
- **Token Expiration**: 1-hour access tokens, 30-day refresh tokens
- **2FA/TOTP**: Time-based one-time passwords
- **Session Management**: Secure logout

### 5. Access Control
- **RBAC**: Three-tier role system
- **Permission Checks**: API enforces permissions
- **Resource Ownership**: Users can only access their documents
- **Audit Logging**: All actions logged with IP and timestamp

### 6. HTTPS Security
- **TLS Encryption**: All communication encrypted
- **Certificate Validation**: Self-signed for development
- **CORS Headers**: Restrict cross-origin requests
- **Secure Headers**: Protection against common attacks

## 🔍 Wireshark MITM Demonstration

### Demonstrating HTTPS vs HTTP Protection

#### Part 1: Capture HTTP Traffic (Vulnerable)

1. **Disable HTTPS Temporarily**
   - Edit `backend/app.py` line 50: Remove SSL context
   - Restart server on port 8000

2. **Open Wireshark**
   - Start packet capture on loopback (127.0.0.1)
   - Filter: `tcp.port == 8000`

3. **Perform HTTP Login**
   - Navigate to `http://localhost:8000`
   - Enter login credentials
   - Go to Documents page

4. **Analyze Traffic**
   - In Wireshark, find HTTP POST requests
   - Look for credentials in plain text
   - Inspect document download traffic
   - Show unencrypted file content

#### Part 2: Capture HTTPS Traffic (Protected)

1. **Re-enable HTTPS**
   - Restart server with SSL context
   - Port 5000

2. **Start New Wireshark Capture**
   - Filter: `tcp.port == 5000`

3. **Perform HTTPS Login**
   - Navigate to `https://localhost:5000`
   - Enter login credentials
   - Go to Documents page

4. **Analyze Traffic**
   - In Wireshark, find HTTPS packets
   - Show that content is encrypted
   - Demonstrate TLS handshake
   - Show encrypted Application Data
   - Verify credentials are NOT visible
   - Show file downloads are encrypted

### MITM Attack Simulation

**Using mitmproxy** (if available):

1. **Start mitmproxy**
   ```bash
   mitmproxy --listen-port 8080
   ```

2. **Configure HTTP Traffic**
   - Set proxy to localhost:8080
   - Attempt HTTP login
   - Show captured credentials in mitmproxy

3. **Attempt HTTPS Interception**
   - Try same with HTTPS
   - Show certificate pinning/validation failure
   - Demonstrate HTTPS protection

### Wireshark Findings Summary

**HTTP (Vulnerable)**
```
- Username visible in plain text
- Password visible in plain text  
- Document content readable
- Easily exploitable by attacker
- No confidentiality
```

**HTTPS (Protected)**
```
- TLS Handshake visible (negotiation only)
- All payload data encrypted
- Certificate validation required
- MITM attack prevented
- Full confidentiality
```

## 📊 Database Schema

### Users Table
```sql
- id (UUID)
- username (VARCHAR, unique)
- email (VARCHAR, unique)
- password_hash (VARCHAR)
- role (VARCHAR) - admin/manager/user
- two_factor_enabled (BOOLEAN)
- two_factor_secret (VARCHAR)
- github_id / google_id (VARCHAR)
- is_active (BOOLEAN)
- created_at, last_login (DATETIME)
```

### Documents Table
```sql
- id (UUID)
- user_id (FK to Users)
- original_filename (VARCHAR)
- stored_filename (VARCHAR)
- file_type (VARCHAR)
- file_size (INTEGER)
- encrypted (BOOLEAN)
- encryption_algorithm (VARCHAR)
- encryption_key_salt (VARCHAR)
- sha256_hash (VARCHAR, unique)
- digital_signature (TEXT)
- signature_algorithm (VARCHAR)
- description (TEXT)
- is_verified (BOOLEAN)
- is_modified (BOOLEAN)
- created_at, updated_at (DATETIME)
```

### AuditLogs Table
```sql
- id (UUID)
- user_id (FK to Users)
- action (VARCHAR)
- resource_type (VARCHAR)
- resource_id (VARCHAR)
- details (TEXT)
- ip_address (VARCHAR)
- timestamp (DATETIME)
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout
- `POST /api/auth/2fa/setup` - Setup 2FA
- `POST /api/auth/2fa/verify` - Verify 2FA
- `POST /api/auth/2fa/verify-login` - Verify 2FA during login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/change-password` - Change password

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/documents/<id>/metadata` - Get document metadata
- `GET /api/documents/<id>/download` - Download document
- `GET /api/documents/<id>/verify` - Verify document
- `DELETE /api/documents/<id>` - Delete document

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/<id>/role` - Update user role
- `PUT /api/admin/users/<id>/status` - Update user status
- `DELETE /api/admin/users/<id>` - Delete user
- `GET /api/admin/audit-logs` - Get audit logs
- `GET /api/admin/statistics` - Get system statistics

## 🛠️ Troubleshooting

### Certificate Issues
```
Q: Browser shows "Your connection is not private"
A: This is normal for self-signed certs. Click "Advanced" → "Proceed"

Q: Certificate error on Windows
A: Run generate_certs.py again, ensure OpenSSL is in PATH
```

### Database Issues
```
Q: "Unable to connect to database"
A: Delete vault.db and restart server to reinitialize

Q: "Table already exists"
A: Database is already initialized, this is normal
```

### Login Issues
```
Q: "Invalid username or password" even with correct credentials
A: Ensure account is created via registration page

Q: 2FA not working
A: Use authenticator app (Google Authenticator, Authy)
A: Time on computer must be synchronized
```

### HTTPS Issues
```
Q: "Failed to connect" on HTTPS
A: Ensure certificates exist in /certificates folder
A: Check port 5000 is not in use: netstat -ano | findstr :5000

Q: "Mixed content" error
A: Ensure all requests go to https://localhost:5000
```

## 📚 Additional Resources

### Security Best Practices
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CWE Top 25: https://cwe.mitre.org/top25/

### Cryptography
- PBKDF2: https://tools.ietf.org/html/rfc2898
- AES: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
- HMAC: https://en.wikipedia.org/wiki/HMAC

### Tools
- Wireshark: https://www.wireshark.org/
- mitmproxy: https://mitmproxy.org/
- OpenSSL: https://www.openssl.org/

## 📝 Notes

### Development Only
- Self-signed certificates are for development only
- Production requires proper CA-signed certificates
- Change SECRET_KEY in production
- Use strong, random JWT_SECRET_KEY
- Enable HTTPS certificate pinning in production

### Data Retention
- Documents stored in `/uploads` folder
- Database stored as `vault.db`
- All files encrypted before storage
- Audit logs retained indefinitely (can be archived)

### Scalability
- SQLite is suitable for development/testing
- Production should use PostgreSQL or MySQL
- Consider document storage on S3 or similar
- Implement caching (Redis) for performance

## 👨‍💻 Development Team

- **Project**: Secure Document Vault System
- **Purpose**: Educational - Data Integrity & Authentication
- **Course**: Level 3, Semester 2
- **Technologies**: Python, Flask, SQLite, JavaScript

## 📄 License

This project is for educational purposes.

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Review server logs in terminal

---

**Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Production Ready for Educational Use
