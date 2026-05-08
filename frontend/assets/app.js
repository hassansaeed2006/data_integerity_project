// API Base URL (use same host/protocol as the page)
const API_BASE = `${window.location.origin}/api`;

// Application State
let appState = {
    user: null,
    token: null,
    refreshToken: null,
    tempToken: null,
    requires2FA: false
};

// ============ Utility Functions ============

function showMessage(elementId, message, type = 'error') {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = `message show ${type}`;
        setTimeout(() => {
            element.classList.remove('show');
        }, 5000);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Show selected page
    const pageName = page.replace('#', '');
    const pageElement = document.getElementById(`${pageName}-page`);
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Update URL
    window.location.hash = page;
    
    // Load page data
    switch(pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'security':
            load2FAStatus();
            break;
        case 'admin':
            loadAdminPanel();
            break;
    }
}

function isAuthenticated() {
    return !!appState.token;
}

function updateNavigation() {
    const loginLink = document.getElementById('nav-login');
    const registerLink = document.getElementById('nav-register');
    const userMenu = document.getElementById('user-menu');
    const adminLink = document.getElementById('nav-admin');
    
    if (isAuthenticated()) {
        loginLink.style.display = 'none';
        registerLink.style.display = 'none';
        userMenu.style.display = 'flex';
        
        // Show admin link only for admins
        if (appState.user && appState.user.role === 'admin') {
            adminLink.style.display = 'block';
        } else {
            adminLink.style.display = 'none';
        }
    } else {
        loginLink.style.display = 'block';
        registerLink.style.display = 'block';
        userMenu.style.display = 'none';
        adminLink.style.display = 'none';
    }
}

// ============ API Functions ============

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (appState.token) {
        options.headers['Authorization'] = `Bearer ${appState.token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============ Authentication ============

// Handle hash navigation
window.addEventListener('hashchange', () => {
    const page = window.location.hash || '#home';
    navigateTo(page);
});

// Load saved token on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
        appState.token = savedToken;
        appState.user = JSON.parse(savedUser);
        updateNavigation();
        navigateTo('#dashboard');
    }
    
    // Navigation links
    document.getElementById('nav-login').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#login');
    });
    
    document.getElementById('nav-register').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#register');
    });
    
    document.getElementById('nav-dashboard').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#dashboard');
    });
    
    document.getElementById('nav-documents').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#documents');
    });
    
    document.getElementById('nav-profile').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#profile');
    });
    
    document.getElementById('nav-admin').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('#admin');
    });
    
    document.getElementById('nav-logout').addEventListener('click', (e) => {
        e.preventDefault();
        logout();
    });
    
    // Forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('upload-form').addEventListener('submit', handleUpload);
    document.getElementById('change-password-form').addEventListener('submit', handleChangePassword);
    document.getElementById('2fa-setup-btn').addEventListener('click', setup2FA);
    document.getElementById('2fa-verify-form').addEventListener('submit', verify2FA);
});

async function handleLogin(e) {
    e.preventDefault();

    // After initial login challenge, reuse the same submit button for OTP verification.
    if (appState.requires2FA) {
        return handleLogin2FA(e);
    }
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const result = await apiCall('/auth/login', 'POST', { username, password });
        
        if (result.requires_2fa) {
            appState.tempToken = result.temp_token;
            appState.requires2FA = true;
            document.getElementById('login-2fa-section').style.display = 'block';
            showMessage('login-message', 'Enter your 2FA code', 'info');
            return;
        }
        
        appState.token = result.access_token;
        appState.refreshToken = result.refresh_token;
        appState.user = result.user;
        
        localStorage.setItem('token', appState.token);
        localStorage.setItem('user', JSON.stringify(appState.user));
        
        updateNavigation();
        showNotification('Login successful!', 'success');
        navigateTo('#dashboard');
    } catch (error) {
        showMessage('login-message', error.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const result = await apiCall('/auth/register', 'POST', {
            username,
            email,
            password
        });
        
        showMessage('register-message', result.message, 'success');
        document.getElementById('register-form').reset();
        
        setTimeout(() => {
            navigateTo('#login');
        }, 2000);
    } catch (error) {
        showMessage('register-message', error.message, 'error');
    }
}

async function handleLogin2FA(e) {
    e.preventDefault();
    
    const token = document.getElementById('login-2fa-code').value;
    
    try {
        const result = await apiCall('/auth/2fa/verify-login', 'POST', {
            token,
            temp_token: appState.tempToken
        });
        
        appState.token = result.access_token;
        appState.refreshToken = result.refresh_token;
        appState.user = result.user;
        appState.requires2FA = false;
        appState.tempToken = null;
        document.getElementById('login-2fa-section').style.display = 'none';
        
        localStorage.setItem('token', appState.token);
        localStorage.setItem('user', JSON.stringify(appState.user));
        
        updateNavigation();
        showNotification('Login successful!', 'success');
        navigateTo('#dashboard');
    } catch (error) {
        showMessage('login-message', error.message, 'error');
    }
}

function logout() {
    apiCall('/auth/logout', 'POST');
    
    appState.token = null;
    appState.user = null;
    appState.tempToken = null;
    appState.requires2FA = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    const login2FASection = document.getElementById('login-2fa-section');
    if (login2FASection) {
        login2FASection.style.display = 'none';
    }
    
    updateNavigation();
    showNotification('Logged out successfully', 'success');
    navigateTo('#home');
}

// ============ Dashboard ============

async function loadDashboard() {
    if (!isAuthenticated()) return;
    
    try {
        // Get current user
        const userResult = await apiCall('/auth/me', 'GET');
        appState.user = userResult.user;
        
        document.getElementById('dashboard-username').textContent = `Username: ${userResult.user.username}`;
        document.getElementById('dashboard-email').textContent = `Email: ${userResult.user.email}`;
        document.getElementById('dashboard-role').textContent = `Role: ${userResult.user.role.toUpperCase()}`;
        
        // Get document count
        try {
            const docsResult = await apiCall('/api/documents', 'GET');
            const userDocs = docsResult.documents.filter(d => d.owner_id === userResult.user.id);
            document.getElementById('dashboard-doc-count').textContent = `Documents: ${userDocs.length}`;
        } catch (e) {
            document.getElementById('dashboard-doc-count').textContent = 'Documents: 0';
        }
        
        // Get 2FA status
        if (userResult.user.two_factor_enabled) {
            document.getElementById('dashboard-2fa-status').textContent = '✓ 2FA Enabled';
        } else {
            document.getElementById('dashboard-2fa-status').textContent = '✗ 2FA Disabled';
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// ============ Documents ============

async function handleUpload(e) {
    e.preventDefault();
    
    const file = document.getElementById('upload-file').files[0];
    const description = document.getElementById('upload-description').value;
    
    if (!file) {
        showMessage('upload-message', 'Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    
    try {
        const options = {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${appState.token}`
            },
            body: formData
        };
        
        const response = await fetch(`${API_BASE}/documents/upload`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error);
        }
        
        showMessage('upload-message', 'Document uploaded and encrypted successfully!', 'success');
        document.getElementById('upload-form').reset();
        
        setTimeout(() => {
            loadDocuments();
        }, 1000);
    } catch (error) {
        showMessage('upload-message', error.message, 'error');
    }
}

async function loadDocuments() {
    if (!isAuthenticated()) return;
    
    try {
        const result = await apiCall('/documents', 'GET');
        const list = document.getElementById('documents-list');
        
        if (!result.documents || result.documents.length === 0) {
            list.innerHTML = '<p>No documents yet. Upload one to get started!</p>';
            return;
        }
        
        list.innerHTML = '';
        result.documents.forEach(doc => {
            // Only show own documents for regular users
            if (appState.user.role !== 'admin' && appState.user.role !== 'manager') {
                if (doc.owner_id !== appState.user.id) return;
            }
            
            const div = document.createElement('div');
            div.className = 'document-item';
            div.innerHTML = `
                <div class="document-info">
                    <h4>${escapeHtml(doc.filename)}</h4>
                    <small>Owner: ${doc.owner}</small>
                    <small>Type: ${doc.file_type.toUpperCase()} | Size: ${formatFileSize(doc.file_size)}</small>
                    <small>Uploaded: ${new Date(doc.created_at).toLocaleString()}</small>
                    <small>Status: ${doc.is_verified ? '✓ Verified' : '✗ Unverified'}</small>
                </div>
                <div class="document-actions">
                    <button class="btn btn-secondary" onclick="viewDocumentDetail('${doc.id}')">Details</button>
                    <button class="btn btn-secondary" onclick="downloadDocument('${doc.id}')">Download</button>
                    <button class="btn btn-secondary" onclick="verifyDocument('${doc.id}')">Verify</button>
                    ${doc.owner_id === appState.user.id || appState.user.role === 'admin' ? `<button class="btn btn-danger" onclick="deleteDocument('${doc.id}')">Delete</button>` : ''}
                </div>
            `;
            list.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading documents:', error);
        document.getElementById('documents-list').innerHTML = `<p>Error loading documents: ${error.message}</p>`;
    }
}

async function viewDocumentDetail(docId) {
    try {
        const result = await apiCall(`/documents/${docId}/metadata`, 'GET');
        const doc = result.document;
        
        const content = document.getElementById('document-detail-content');
        content.innerHTML = `
            <h3>${escapeHtml(doc.filename)}</h3>
            <div class="document-detail">
                <div class="metadata-item">
                    <strong>Owner:</strong>
                    <span>${doc.owner}</span>
                </div>
                <div class="metadata-item">
                    <strong>File Type:</strong>
                    <span>${doc.file_type.toUpperCase()}</span>
                </div>
                <div class="metadata-item">
                    <strong>File Size:</strong>
                    <span>${formatFileSize(doc.file_size)}</span>
                </div>
                <div class="metadata-item">
                    <strong>Created:</strong>
                    <span>${new Date(doc.created_at).toLocaleString()}</span>
                </div>
                <div class="metadata-item">
                    <strong>Last Updated:</strong>
                    <span>${new Date(doc.updated_at).toLocaleString()}</span>
                </div>
                <div class="metadata-item">
                    <strong>Encrypted:</strong>
                    <span>${doc.encrypted ? 'Yes (' + doc.encryption_algorithm + ')' : 'No'}</span>
                </div>
                <div class="metadata-item">
                    <strong>Verification Status:</strong>
                    <span>${doc.is_verified ? '✓ Verified' : '✗ Not Verified'}</span>
                </div>
                <div class="metadata-item">
                    <strong>Modified:</strong>
                    <span>${doc.is_modified ? 'Yes ⚠️' : 'No'}</span>
                </div>
                <div class="metadata-item">
                    <strong>SHA-256 Hash:</strong>
                    <code>${doc.sha256_hash}</code>
                </div>
                <div class="metadata-item">
                    <strong>Digital Signature:</strong>
                    <code>${doc.digital_signature || 'N/A'}</code>
                </div>
                <div class="metadata-item">
                    <strong>Description:</strong>
                    <span>${doc.description || 'N/A'}</span>
                </div>
            </div>
        `;
        
        navigateTo('#document-detail');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function downloadDocument(docId) {
    try {
        const options = {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${appState.token}`
            }
        };
        
        const response = await fetch(`${API_BASE}/documents/${docId}/download`, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }
        
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition ? contentDisposition.split('filename=')[1].trim('"') : 'document';
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
        showNotification('Document downloaded successfully', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function verifyDocument(docId) {
    try {
        const result = await apiCall(`/documents/${docId}/verify`, 'GET');
        const verification = result.verification;
        
        let message = `
Document Verification Report
=============================
Filename: ${verification.filename}
Overall Status: ${verification.overall_status}

Integrity Check:
- Valid: ${verification.integrity_check.valid ? 'YES' : 'NO'}
- Original Hash: ${verification.integrity_check.original_hash}
- Current Hash: ${verification.integrity_check.current_hash}

Signature Check:
- Valid: ${verification.signature_check.valid ? 'YES' : 'NO'}
- Algorithm: ${verification.signature_check.algorithm}

Verified at: ${verification.verified_at}
        `;
        
        alert(message);
        loadDocuments();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document? This cannot be undone.')) {
        return;
    }
    
    try {
        await apiCall(`/documents/${docId}`, 'DELETE');
        showNotification('Document deleted successfully', 'success');
        loadDocuments();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// ============ Profile & Security ============

async function handleChangePassword(e) {
    e.preventDefault();
    
    const oldPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    
    try {
        const result = await apiCall('/auth/change-password', 'POST', {
            old_password: oldPassword,
            new_password: newPassword
        });
        
        showMessage('password-message', result.message, 'success');
        document.getElementById('change-password-form').reset();
    } catch (error) {
        showMessage('password-message', error.message, 'error');
    }
}

async function load2FAStatus() {
    try {
        const result = await apiCall('/auth/me', 'GET');
        const statusDiv = document.getElementById('2fa-status');
        
        if (result.user.two_factor_enabled) {
            statusDiv.innerHTML = '<p>✓ Two-Factor Authentication is <strong>ENABLED</strong></p>';
            document.getElementById('2fa-setup-btn').style.display = 'none';
        } else {
            statusDiv.innerHTML = '<p>✗ Two-Factor Authentication is <strong>DISABLED</strong></p>';
            document.getElementById('2fa-setup-btn').style.display = 'block';
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function setup2FA() {
    try {
        const result = await apiCall('/auth/2fa/setup', 'POST');
        
        document.getElementById('2fa-section').style.display = 'block';
        document.getElementById('2fa-qr').innerHTML = `<img src="data:image/png;base64,${result.qr_code}" alt="2FA QR Code">`;
        document.getElementById('2fa-secret').textContent = result.secret;
    } catch (error) {
        showMessage('2fa-message', error.message, 'error');
    }
}

async function verify2FA(e) {
    e.preventDefault();
    
    const token = document.getElementById('2fa-verify-code').value;
    
    try {
        const result = await apiCall('/auth/2fa/verify', 'POST', { token });
        
        showMessage('2fa-message', result.message, 'success');
        document.getElementById('2fa-verify-form').reset();
        
        setTimeout(() => {
            load2FAStatus();
            document.getElementById('2fa-section').style.display = 'none';
        }, 1500);
    } catch (error) {
        showMessage('2fa-message', error.message, 'error');
    }
}

// ============ Admin Panel ============

async function loadAdminPanel() {
    if (!isAuthenticated() || appState.user.role !== 'admin') {
        showNotification('Admin access required', 'error');
        return;
    }
    
    loadAdminStatistics();
    loadUsersList();
    loadAuditLogs();
}

async function loadAdminStatistics() {
    try {
        const result = await apiCall('/admin/statistics', 'GET');
        const statsDiv = document.getElementById('admin-stats');
        
        statsDiv.innerHTML = `
            <div class="stat-card">
                <h4>${result.users.total}</h4>
                <p>Total Users</p>
            </div>
            <div class="stat-card">
                <h4>${result.users.active}</h4>
                <p>Active Users</p>
            </div>
            <div class="stat-card">
                <h4>${result.user_roles.admins}</h4>
                <p>Administrators</p>
            </div>
            <div class="stat-card">
                <h4>${result.user_roles.managers}</h4>
                <p>Managers</p>
            </div>
            <div class="stat-card">
                <h4>${result.documents.total}</h4>
                <p>Total Documents</p>
            </div>
            <div class="stat-card">
                <h4>${result.documents.encrypted}</h4>
                <p>Encrypted Documents</p>
            </div>
            <div class="stat-card">
                <h4>${result.documents.verified}</h4>
                <p>Verified Documents</p>
            </div>
            <div class="stat-card">
                <h4>${result.audit_logs}</h4>
                <p>Audit Log Entries</p>
            </div>
        `;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

async function loadUsersList() {
    try {
        const result = await apiCall('/admin/users', 'GET');
        const usersDiv = document.getElementById('users-list');
        
        if (!result.users || result.users.length === 0) {
            usersDiv.innerHTML = '<p>No users found</p>';
            return;
        }
        
        let html = '<table><thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Status</th><th>2FA</th><th>Last Login</th><th>Actions</th></tr></thead><tbody>';
        
        result.users.forEach(user => {
            html += `
                <tr>
                    <td>${escapeHtml(user.username)}</td>
                    <td>${escapeHtml(user.email)}</td>
                    <td>${user.role}</td>
                    <td>${user.is_active ? '✓ Active' : '✗ Inactive'}</td>
                    <td>${user.two_factor_enabled ? '✓ Enabled' : 'Disabled'}</td>
                    <td>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                    <td>
                        <div class="user-actions">
                            <select onchange="updateUserRole('${user.id}', this.value)" class="role-select">
                                <option value="user" ${user.role === 'user' ? 'selected' : ''}>User</option>
                                <option value="manager" ${user.role === 'manager' ? 'selected' : ''}>Manager</option>
                                <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                            </select>
                            <button class="btn btn-secondary" onclick="toggleUserStatus('${user.id}', ${!user.is_active})">${user.is_active ? 'Deactivate' : 'Activate'}</button>
                            ${user.id !== appState.user.id ? `<button class="btn btn-danger" onclick="deleteUser('${user.id}', '${escapeHtml(user.username)}')">Delete</button>` : ''}
                        </div>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        usersDiv.innerHTML = html;
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function updateUserRole(userId, newRole) {
    try {
        const result = await apiCall(`/admin/users/${userId}/role`, 'PUT', { role: newRole });
        showNotification('User role updated successfully', 'success');
        loadUsersList();
    } catch (error) {
        showNotification(error.message, 'error');
        loadUsersList();
    }
}

async function toggleUserStatus(userId, activate) {
    try {
        await apiCall(`/admin/users/${userId}/status`, 'PUT', { is_active: activate });
        showNotification(`User ${activate ? 'activated' : 'deactivated'} successfully`, 'success');
        loadUsersList();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"? This cannot be undone.`)) {
        return;
    }
    
    try {
        await apiCall(`/admin/users/${userId}`, 'DELETE');
        showNotification('User deleted successfully', 'success');
        loadUsersList();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function loadAuditLogs() {
    try {
        const result = await apiCall('/admin/audit-logs?limit=50', 'GET');
        const logsDiv = document.getElementById('audit-logs');
        
        if (!result.logs || result.logs.length === 0) {
            logsDiv.innerHTML = '<p>No audit logs found</p>';
            return;
        }
        
        logsDiv.innerHTML = '';
        result.logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'audit-log-item';
            div.innerHTML = `
                <strong>${log.action}</strong> - ${log.resource_type}${log.resource_id ? ` (${log.resource_id})` : ''}
                <small>User: ${log.username} | Time: ${new Date(log.timestamp).toLocaleString()} | IP: ${log.ip_address}</small>
            `;
            logsDiv.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading audit logs:', error);
    }
}

// ============ Utility Functions ============

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
