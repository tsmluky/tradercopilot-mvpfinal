import sys
import os

# Adjust path to find backend modules
current_dir = os.getcwd()
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

try:
    from core.security import get_password_hash
    print("Hashing 'admin'...")
    h = get_password_hash("admin")
    print(f"Success: {h}")
except Exception as e:
    print(f"Error: {e}")
