# Certificate Expiry Simulation

Provides a helper to generate expired TLS certificates for testing.

## Prerequisites

- Python package: `cryptography`.

## Usage

1. Generate the expired cert and key.
2. Replace the service certificate in a test environment.
3. Roll back to a valid cert after the experiment.

## Verification

- Confirm clients receive a certificate expiry error.
- Validate recovery once the valid cert is restored.

```python
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def create_expired_certificate(
    common_name: str,
    expired_days_ago: int = 1
) -> tuple[bytes, bytes]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    not_valid_before = datetime.utcnow() - timedelta(days=365)
    not_valid_after = datetime.utcnow() - timedelta(days=expired_days_ago)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name)
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        not_valid_before
    ).not_valid_after(
        not_valid_after
    ).sign(private_key, hashes.SHA256())

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return cert_pem, key_pem
```
