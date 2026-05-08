#!/usr/bin/env python3
"""
Generate self-signed HTTPS certificates for development
This creates a certificate valid for 365 days
"""

import os
import subprocess
import sys
import socket

cert_dir = os.path.dirname(os.path.abspath(__file__))
force_regen = '--force' in sys.argv


def detect_local_ips():
    """Return non-loopback IPv4 addresses for SAN."""
    ips = set()
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith('127.'):
                ips.add(ip)
    except Exception:
        pass
    return sorted(ips)

# Check if OpenSSL is available
if subprocess.run(['where' if os.name == 'nt' else 'which', 'openssl'], 
                   capture_output=True).returncode != 0:
    print("ERROR: OpenSSL is not installed or not in PATH")
    print("Install OpenSSL and try again")
    sys.exit(1)

cert_path = os.path.join(cert_dir, 'cert.pem')
key_path = os.path.join(cert_dir, 'key.pem')

# Check if certificates already exist
if os.path.exists(cert_path) and os.path.exists(key_path) and not force_regen:
    print("Certificates already exist at:")
    print(f"  Certificate: {cert_path}")
    print(f"  Private Key: {key_path}")
    print("\nUse --force to regenerate with updated SAN entries.")
    sys.exit(0)

print("Generating self-signed HTTPS certificates...")
print("This will create a certificate valid for 365 days")

# Build SAN list so HTTPS works on localhost and LAN IP access.
dns_names = ['localhost']
ip_addresses = ['127.0.0.1'] + detect_local_ips()
san_entries = [f'DNS:{name}' for name in dns_names] + [f'IP:{ip}' for ip in ip_addresses]
san_value = ','.join(san_entries)
common_name = ip_addresses[1] if len(ip_addresses) > 1 else 'localhost'

print("Certificate SAN entries:")
for entry in san_entries:
    print(f"  - {entry}")

# Generate certificate and key
cmd = [
    'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
    '-keyout', key_path,
    '-out', cert_path,
    '-days', '365',
    '-nodes',
    '-subj', f'/C=US/ST=State/L=City/O=Organization/CN={common_name}',
    '-addext', f'subjectAltName={san_value}'
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✓ Certificates generated successfully!")
        print(f"  Certificate: {cert_path}")
        print(f"  Private Key: {key_path}")
        print("\nIMPORTANT: This is a self-signed certificate for development only.")
        print("Your browser will show a security warning - this is normal and expected.")
        print("In production, use a certificate from a trusted Certificate Authority.")
    else:
        print(f"ERROR: Certificate generation failed")
        print(f"OpenSSL error: {result.stderr}")
        sys.exit(1)

except subprocess.TimeoutExpired:
    print("ERROR: Certificate generation timed out")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
