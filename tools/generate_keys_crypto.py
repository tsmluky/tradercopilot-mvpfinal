from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

def to_base64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

# Generate EC Key (P-256)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Serialize Private Key (32 bytes raw scalar)
private_val = private_key.private_numbers().private_value
private_bytes = private_val.to_bytes(32, byteorder='big')
private_b64 = to_base64url(private_bytes)

# Serialize Public Key (Uncompressed Point format: 0x04 + x + y)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
public_b64 = to_base64url(public_bytes)

with open("tools/vapid_keys.txt", "w") as f:
    f.write(f"VAPID_PRIVATE_KEY={private_b64}\n")
    f.write(f"VAPID_PUBLIC_KEY={public_b64}\n")
print("Keys written to tools/vapid_keys.txt")
