
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

def generate_vapid_keys():
    # Helper to convert to URL-safe base64 without padding (VAPID format)
    def to_b64url(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=')

    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Private Key (Integer) - but usually pywebpush accepts PEM or DER path
    # Let's export as PEM for .env file usually
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Public Key (Uncompressed Point)
    public_numbers = public_key.public_numbers()
    x = public_numbers.x.to_bytes(32, 'big')
    y = public_numbers.y.to_bytes(32, 'big')
    # Uncompressed starts with 0x04
    public_bytes = b'\x04' + x + y
    
    # pywebpush expects "raw" bytes b64 encoded for "vapid_private_key" in some contexts?
    # standard format is often just the private number for some libs, but sticking to PEM is safer for server.
    # For Frontend, we strictly need the Public Key in URL-Safe Base64
    
    public_b64 = to_b64url(public_bytes)

    # For Private key, let's keep it as PEM string for env variable (easy to load)
    # or base64 of the private number. pywebpush accepts PEM file path or string.
    
    print("VAPID Keys Generated:")
    print("---------------------")
    print(f"VAPID_PRIVATE_KEY={private_pem.decode('utf-8').replace(chr(10), '')}") # Flatten for single line env if needed, or keep newlines
    print(f"VAPID_PUBLIC_KEY={public_b64.decode('utf-8')}")
    print(f"VAPID_MAIL=mailto:admin@tradercopilot.com")
    
    # Note: Private PEM usually has headers. For .env, sometimes it's easier to point to a file.
    # But let's try to provide it as a single line string to avoid parsing headaches, or just save to a file.
    
    with open("vapid_private.pem", "wb") as f:
        f.write(private_pem)
    print("\n(Private key also saved to 'vapid_private.pem' for convenience)")

if __name__ == "__main__":
    generate_vapid_keys()
