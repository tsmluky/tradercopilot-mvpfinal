
from pywebpush import VAPID

def generate_vapid():
    vapid = VAPID()
    vapid.generate_keys()
    
    print("VAPID Keys Generated:")
    print(f"VAPID_PRIVATE_KEY={vapid.private_key_pem.decode('utf-8').strip()}")
    print("-" * 20)
    print(f"VAPID_PUBLIC_KEY={vapid.public_key_pem.decode('utf-8').strip()}")
    print(f"VAPID_MAIL=mailto:admin@tradercopilot.com")

if __name__ == "__main__":
    generate_vapid()
