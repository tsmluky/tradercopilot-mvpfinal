import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import backend.marketplace_config...")
    from backend import marketplace_config
    print("Import successful!")
    print(f"Strategies found: {len(marketplace_config.MARKETPLACE_PERSONAS)}")
except Exception as e:
    print(f"FATAL ERROR importing config: {e}")
    import traceback
    traceback.print_exc()
