from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

# Generowanie klucza prywatnego
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Generowanie certyfikatu SSL
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, u"192.168.1.10"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(datetime.timezone.utc)
).not_valid_after(
    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
).sign(key, hashes.SHA256())

# Zapis klucza do key.pem
with open("key.pem", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Zapis certyfikatu do cert.pem
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Pomyślnie wygenerowano pliki cert.pem oraz key.pem!")