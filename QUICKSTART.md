# Quick Start Guide - Secure Document Vault

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Generate Certificates
```bash
cd certificates
python generate_certs.py
cd ..
```

### Step 3: Run the Application
```bash
cd backend
python app.py
```

### Step 4: Access in Browser
```
https://localhost:5000
```

Click through the security warning (expected for self-signed certs).

---

## 📝 First Steps After Starting

1. **Create an Admin Account**
   - Register: Username: `admin`, Email: `admin@test.local`, Password: `SecurePass123!`
   - You now have admin access

2. **Create a Test User**
   - Register: Username: `testuser`, Email: `test@test.local`, Password: `SecurePass123!`
   - Regular user account for testing

3. **Try the Features**
   - Upload a document (PDF, text file, etc.)
   - Download and verify the document
   - Check document details and metadata

4. **Enable 2FA**
   - Go to Security Settings
   - Click "Setup 2FA"
   - Scan QR code with Google Authenticator or Authy
   - Enter the 6-digit code to enable

5. **Test Admin Panel**
   - Login as admin
   - Click "Admin" in navigation
   - View statistics, manage users, see audit logs

---

## 🔐 Key Features to Test

### Authentication
- [ ] User registration with password validation
- [ ] Login with JWT tokens
- [ ] 2FA setup and verification
- [ ] Password change
- [ ] Logout

### Documents
- [ ] Upload document (auto-encrypted)
- [ ] View document metadata
- [ ] Download document (auto-decrypted)
- [ ] Verify document integrity
- [ ] Check digital signature
- [ ] Delete document

### Admin Features (if logged in as admin)
- [ ] View system statistics
- [ ] Manage user roles
- [ ] Activate/deactivate users
- [ ] View audit logs
- [ ] Delete users

### Security
- [ ] Passwords hashed with bcrypt
- [ ] Documents encrypted with AES-256
- [ ] Integrity verified with SHA-256 hashes
- [ ] All traffic on HTTPS
- [ ] All actions logged to audit trail

---

## 🧪 Test Accounts

After registration:

| Username | Password | Role |
|----------|----------|------|
| admin | SecurePass123! | Admin |
| manager | SecurePass123! | Manager |
| testuser | SecurePass123! | User |

---

## 📊 Project Structure
```
project/
├── backend/
│   ├── app.py              # Main Flask app
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── security_utils.py   # Encryption, hashing, RBAC
│   ├── auth_routes.py      # Authentication endpoints
│   ├── document_routes.py  # Document management endpoints
│   ├── admin_routes.py     # Admin endpoints
│   ├── requirements.txt    # Python dependencies
│   └── vault.db            # SQLite database (auto-created)
│
├── frontend/
│   ├── index.html          # Main HTML
│   └── assets/
│       ├── style.css       # Styling
│       └── app.js          # JavaScript application
│
├── certificates/
│   ├── generate_certs.py   # Certificate generator
│   ├── cert.pem            # Self-signed cert (auto-created)
│   └── key.pem             # Private key (auto-created)
│
├── uploads/                # Encrypted documents storage
├── README.md               # Full documentation
└── .env.example            # Environment template
```

---

## 🚨 Common Issues & Solutions

### Issue: "Address already in use"
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "Certificate verification failed"
- This is normal for self-signed certs
- Click "Advanced" → "Proceed"

### Issue: "ModuleNotFoundError"
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### Issue: "Password doesn't meet policy"
- Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
- Example: `SecurePass123!`

---

## 📱 Browser Compatibility

✅ **Tested & Working**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

**Important**: Must use HTTPS-capable browser

---

## 🔍 Testing Wireshark (Optional)

### HTTP (Vulnerable)
```
1. Open Wireshark
2. Disable HTTPS (comment SSL context in app.py)
3. Run on port 8000
4. Capture traffic
5. See credentials in plain text
```

### HTTPS (Protected)
```
1. Restart with HTTPS enabled
2. Capture traffic
3. See encrypted data only
4. Show TLS handshake
```

---

## 📚 Documentation Files

- **README.md** - Complete project documentation
- **.env.example** - Environment variables template
- **QUICKSTART.md** - This file

---

## ⏱️ Typical Workflow

1. Start server: `python backend/app.py`
2. Open browser: `https://localhost:5000`
3. Register new user
4. Upload a document
5. Verify document integrity
6. Download and check decryption works
7. Try 2FA setup
8. (Admin) Check audit logs

---

## 💡 Pro Tips

- Use incognito mode for multi-user testing
- Check browser console (F12) for errors
- Check server terminal for detailed logs
- Documents are encrypted immediately upon upload
- Verify checks both hash and signature
- Admin can see and manage all users and documents

---

**Ready to test?** Run `python backend/app.py` and open `https://localhost:5000`

For detailed information, see README.md
