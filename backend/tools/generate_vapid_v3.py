
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

def generate_vapid_keys():
    def to_b64url(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=')

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_numbers = public_key.public_numbers()
    x = public_numbers.x.to_bytes(32, 'big')
    y = public_numbers.y.to_bytes(32, 'big')
    public_bytes = b'\x04' + x + y
    public_b64 = to_b64url(public_bytes).decode('utf-8')

    # Fix: pre-calculate string replacement
    pem_str = private_pem.decode('utf-8').replace('\n', '\\n')

    output = f"""VAPID_PRIVATE_KEY={pem_str}
VAPID_PUBLIC_KEY={public_b64}
VAPID_MAIL=mailto:admin@tradercopilot.com
"""
    with open("vapid_keys_final.txt", "w") as f:
        f.write(output)
    
    print("Keys saved to vapid_keys_final.txt")

if __name__ == "__main__":
    generate_vapid_keys()
