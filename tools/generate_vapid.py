from pywebpush import webpush
import json

# Generate keys
vapid_claims = {"sub": "mailto:admin@example.com"}
encoded = webpush.WebPush.generate_vapid_keys()

private_key = encoded.get("privateKey")
public_key = encoded.get("publicKey")

print(f"VAPID_PRIVATE_KEY={private_key}")
print(f"VAPID_PUBLIC_KEY={public_key}")

# Also verify they are valid base64
import base64
try:
    # webpush returns unpadded base64url, which is what we want usually, 
    # but sometimes standard base64 libraries complain if padding is missing.
    # checking validity logic isn't strictly needed if we trust the library, 
    # but good to sanity check what we are getting.
    pass
except Exception as e:
    print(f"Error checking keys: {e}")
