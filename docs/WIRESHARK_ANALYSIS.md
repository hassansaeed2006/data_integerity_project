# Wireshark MITM Traffic Analysis Guide

## 📡 Objective
Demonstrate the security difference between HTTP (unencrypted) and HTTPS (encrypted) communication using packet capture analysis.

---

## Part 1: HTTP Traffic Analysis (Vulnerable)

### Prerequisites
- Wireshark installed (https://www.wireshark.org/)
- Two terminal windows
- Text editor for configuration

### Step 1: Disable HTTPS in Backend

Edit `backend/app.py` (line ~50):

**Original (HTTPS):**
```python
if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=('certificates/cert.pem', 'certificates/key.pem'),
        debug=False
    )
```

**Change to (HTTP):**
```python
if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
```

### Step 2: Start Wireshark Capture

1. **Open Wireshark**
   - Windows: Start → Wireshark
   - Or command: `wireshark`

2. **Select Loopback Interface**
   - Windows: "Adapter for loopback traffic capture"
   - Linux: "lo"
   - macOS: "lo0"

3. **Start Capture**
   - Click the blue shark fin icon
   - Or Capture → Start

4. **Apply Filter**
   - Type in filter bar: `tcp.port == 8000`
   - Press Enter
   - This shows only traffic on port 8000

### Step 3: Generate HTTP Traffic

1. **Restart Backend (HTTP Mode)**
   ```bash
   cd backend
   python app.py
   ```
   Should show: "Running on http://0.0.0.0:8000"

2. **Open Browser**
   - Navigate to: `http://localhost:8000`

3. **Test Login**
   - Username: `admin`
   - Password: `SecurePass123!`
   - Click Login

4. **Navigate to Documents**
   - Click "Documents" in navigation
   - Upload a test document

### Step 4: Analyze HTTP Capture

#### Finding Login Credentials

1. **In Wireshark**, look for POST requests:
   - Find packet with "POST /api/auth/login"
   - Double-click to expand

2. **View Raw Data**
   - Click "Hypertext Transfer Protocol" section
   - Scroll to request body
   - **You can see in plain text:**
     ```
     {"username":"admin","password":"SecurePass123!"}
     ```

#### Finding Document Content

1. **Look for document uploads:**
   - Search for packets containing file data
   - Can see file content in plain text
   - File binary data partially readable

#### Findings to Document

```
HTTP ANALYSIS FINDINGS:
======================

1. Credentials Exposure
   - Username: VISIBLE in plain text
   - Password: VISIBLE in plain text
   - JSON payload completely exposed
   - Risk: Anyone on network can intercept credentials

2. Document Content
   - File contents: READABLE (plaintext files)
   - Binary files: Partially recoverable
   - Metadata: All visible
   - Risk: Sensitive document content exposed

3. API Responses
   - JWT tokens: VISIBLE
   - User information: ALL FIELDS VISIBLE
   - Document hashes: VISIBLE
   - Risk: Complete API access for attacker

4. Attack Scenario (MITM)
   - Attacker on same network
   - Captures HTTP traffic
   - Extracts credentials
   - Accesses all documents
   - No encryption = CRITICAL RISK
```

### Screenshots to Capture

- [ ] Login request with visible credentials
- [ ] Response with JWT token visible
- [ ] Document upload packet
- [ ] File content in plaintext

---

## Part 2: HTTPS Traffic Analysis (Protected)

### Step 1: Re-enable HTTPS

Edit `backend/app.py` back to:

```python
if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=('certificates/cert.pem', 'certificates/key.pem'),
        debug=False
    )
```

### Step 2: Update Wireshark Filter

1. **Stop current capture** (red square)
2. **Change filter to:**
   ```
   tcp.port == 5000
   ```
3. **Start new capture** (blue shark fin)

### Step 3: Generate HTTPS Traffic

1. **Restart Backend (HTTPS Mode)**
   ```bash
   python app.py
   ```
   Should show: "Running on https://0.0.0.0:5000"

2. **Open Browser**
   - Navigate to: `https://localhost:5000`
   - Accept security warning
   - Click "Advanced" → "Proceed"

3. **Perform Same Actions**
   - Login with admin/SecurePass123!
   - Upload document

### Step 4: Analyze HTTPS Capture

#### TLS Handshake

Look for these packets in order:

1. **Client Hello**
   - First packet from client
   - Plaintext (unencrypted)
   - Contains supported cipher suites
   - Can inspect in Wireshark

2. **Server Hello**
   - Response from server
   - Contains selected cipher suite
   - Certificate exchange

3. **Certificate Exchange**
   - Server sends SSL certificate
   - Can view certificate details
   - Shows: CN=localhost, self-signed

4. **Key Exchange**
   - Client and server exchange keys
   - Algorithm: RSA or ECDH
   - Creates shared session key

5. **Finished**
   - Both sides confirm encryption established

#### Encrypted Data

1. **After handshake, all data is encrypted:**
   ```
   Packet: [Encrypted Application Data]
   Length: XXXX bytes
   Content: @@##$$%%^^ (encrypted, unreadable)
   ```

2. **Try to read encrypted packet:**
   - Right-click packet
   - "Follow → TCP Stream"
   - See: Mostly binary/unreadable data
   - Cannot see credentials
   - Cannot see document content

### Findings to Document

```
HTTPS ANALYSIS FINDINGS:
=======================

1. Credentials Protection
   - Username: ENCRYPTED
   - Password: ENCRYPTED
   - JSON payload: ENCRYPTED
   - Risk: MITIGATED ✓

2. Document Content
   - File contents: ENCRYPTED
   - Binary data: ENCRYPTED
   - Metadata: ENCRYPTED
   - Risk: MITIGATED ✓

3. API Responses
   - JWT tokens: ENCRYPTED
   - User information: ENCRYPTED
   - Document data: ENCRYPTED
   - Risk: MITIGATED ✓

4. TLS Security
   - Handshake: Visible (negotiation)
   - Session key: Encrypted exchange
   - Application data: All encrypted
   - Certificate: Self-signed (for dev)
   - Risk: PROTECTIONS IN PLACE ✓

5. Attack Scenario (MITM)
   - Attacker on same network
   - Captures HTTPS traffic
   - Sees only encrypted data
   - Cannot extract credentials
   - Cannot access documents
   - Cannot intercept session
   - Risk: MITIGATED ✓
```

---

## Comparative Analysis Report

### Create a Document with These Comparisons:

```markdown
# Security Comparison: HTTP vs HTTPS

## HTTP (Port 8000)

### What's Visible
- Username and password in JSON
- Document contents (plaintext)
- File metadata
- JWT tokens
- User personal information
- All API requests/responses

### What's Readable
- Text files: 100%
- Binary files: Partial (headers, format info)
- Credentials: Complete

### Risk Assessment
- CRITICAL: Anyone on network can intercept credentials
- CRITICAL: All documents visible to attacker
- CRITICAL: Session tokens can be stolen
- CRITICAL: Complete data breach possible

## HTTPS (Port 5000)

### What's Visible
- TLS Handshake (encryption negotiation)
- Packet sizes (metadata)
- IP addresses and ports
- Connection start/end

### What's Readable
- Nothing after handshake complete
- All application data encrypted
- No credentials visible
- No document content visible

### Risk Assessment
- LOW: Credentials protected
- LOW: Document content protected
- LOW: Session tokens encrypted
- HIGH CONFIDENCE: Data protected

## Key Findings

1. **Encryption Impact**: HTTP exposes 100% of data, HTTPS exposes 0%
2. **Protocol Overhead**: HTTPS adds ~5% overhead (acceptable for security)
3. **Certificate Validation**: Self-signed works for development, CA-signed needed for production
4. **Man-in-the-Middle Protection**: HTTPS prevents MITM by requiring encryption

## Recommendations

✓ Always use HTTPS in production
✓ Implement certificate pinning for critical apps
✓ Use strong encryption algorithms (TLS 1.3+)
✓ Rotate certificates regularly
✓ Monitor for certificate issues
```

---

## Advanced: Using mitmproxy

### Optional: Deeper MITM Simulation

**Prerequisites**: Install mitmproxy
```bash
pip install mitmproxy
```

### HTTP Interception

1. **Start mitmproxy:**
   ```bash
   mitmproxy --listen-port 8080
   ```

2. **Configure System Proxy:**
   - Windows: Settings → Network → Proxy → 127.0.0.1:8080
   - Or use browser proxy settings

3. **Access HTTP application:**
   ```
   http://localhost:8000
   ```

4. **In mitmproxy interface:**
   - See all requests/responses
   - View credentials in plain text
   - Modify requests
   - Block/allow traffic

### HTTPS Interception Attempt

1. **Access HTTPS application:**
   ```
   https://localhost:5000
   ```

2. **Browser will show:**
   - Certificate error (mitmproxy's cert)
   - Connection blocked
   - Proof that certificate validation prevents MITM

3. **Findings:**
   - HTTPS prevents transparent interception
   - Certificate pinning would prevent even this
   - HTTPS provides protection

---

## Lab Report Template

### Your Wireshark Analysis Should Include:

```
WIRESHARK MITM ANALYSIS REPORT
==============================

Objective: Compare HTTP vs HTTPS security

[1] HTTP Analysis (Port 8000)
  - Screenshots of:
    ✓ Unencrypted credentials
    ✓ Plain text password
    ✓ Document content
    ✓ API responses with tokens
  
  - Findings:
    ✓ What was visible
    ✓ What could be exploited
    ✓ Risk assessment

[2] HTTPS Analysis (Port 5000)
  - Screenshots of:
    ✓ TLS Handshake packets
    ✓ Encrypted application data
    ✓ Certificate exchange
    ✓ Session key negotiation
  
  - Findings:
    ✓ Encryption protection
    ✓ Why MITM is prevented
    ✓ Security improvements

[3] Comparison Matrix
  - HTTP vulnerabilities vs HTTPS protections
  - Risk before/after HTTPS
  - Practical security impact

[4] Conclusion
  - Why HTTPS is critical
  - Real-world implications
  - Best practices
```

---

## Troubleshooting

### "No packets captured"
- Verify correct filter: `tcp.port == 5000` or `tcp.port == 8000`
- Ensure loopback interface selected
- Traffic might be buffered (try stopping/restarting server)

### "Can't see packet details"
- Scroll down in packet details pane
- Expand protocol layers
- Look in "Hypertext Transfer Protocol" section

### "mitmproxy won't intercept HTTPS"
- This is expected! It's proof HTTPS works
- Show the error as evidence of protection

### "Browser still shows HTTP"
- Verify app.py is running on port 8000
- Check terminal shows "Running on http://..."

---

## Educational Value

This exercise demonstrates:

✅ Real security vulnerability (HTTP)
✅ Security solution (HTTPS)
✅ Practical packet analysis
✅ Encryption benefits
✅ MITM attack concepts
✅ Why encryption matters

---

## Deliverables

1. **Wireshark captures** - Screenshots of HTTP and HTTPS traffic
2. **Analysis report** - Findings and comparison
3. **Risk assessment** - Before/after security impact
4. **Conclusions** - What you learned

---

**Time Required**: 30-45 minutes
**Difficulty**: Intermediate
**Tools**: Wireshark, Browser, Terminal
