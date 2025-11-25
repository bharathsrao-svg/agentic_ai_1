"""
Quick script to generate access token from request_token
Usage: python quick_generate_token.py <request_token> [api_secret]
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from kiteconnect import KiteConnect
import re

# Load API key
load_dotenv("api_key.env")

KITE_API_KEY = os.getenv('KITE_API_KEY', 'aybro7iwoafvnmnj')
KITE_API_SECRET = os.getenv('KITE_API_SECRET')

print("=" * 80)
print("GENERATE KITE ACCESS TOKEN")
print("=" * 80)
print()

# Get request_token from command line or input
if len(sys.argv) > 1:
    request_token = sys.argv[1]
else:
    print("You have the request_token from the redirect URL.")
    print("Example: https://your-url.com/?request_token=XXXXX&action=login")
    print()
    request_token = input("Enter request_token: ").strip()

if not request_token:
    print("[ERROR] Request token is required")
    print("Usage: python quick_generate_token.py <request_token> [api_secret]")
    sys.exit(1)

# Get API secret
if len(sys.argv) > 2:
    KITE_API_SECRET = sys.argv[2]
elif not KITE_API_SECRET:
    print()
    print("API Secret is required. Get it from:")
    print("  https://developers.kite.trade -> Your App -> API Secret")
    print()
    KITE_API_SECRET = input("Enter API Secret: ").strip()
    if not KITE_API_SECRET:
        print("[ERROR] API Secret is required")
        sys.exit(1)

print()
print(f"[OK] API Key: {KITE_API_KEY}")
print(f"[OK] Request Token: {request_token[:20]}...")
print()

try:
    print("Generating access token...")
    
    kite = KiteConnect(api_key=KITE_API_KEY)
    data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
    
    access_token = data["access_token"]
    
    print()
    print("=" * 80)
    print("[SUCCESS] Access Token Generated!")
    print("=" * 80)
    print()
    print(f"Access Token: {access_token}")
    print()
    
    # Update api_key.env
    env_file = Path("api_key.env")
    if env_file.exists():
        content = env_file.read_text()
        
        # Update access token
        if 'KITE_ACCESS_TOKEN=' in content:
            content = re.sub(
                r'KITE_ACCESS_TOKEN=.*',
                f'KITE_ACCESS_TOKEN={access_token}',
                content
            )
        else:
            content += f'\nKITE_ACCESS_TOKEN={access_token}\n'
        
        # Update API secret if not set
        if 'KITE_API_SECRET=' not in content or 'your_api_secret_here' in content:
            if 'KITE_API_SECRET=' in content:
                content = re.sub(
                    r'KITE_API_SECRET=.*',
                    f'KITE_API_SECRET={KITE_API_SECRET}',
                    content
                )
            else:
                content += f'\nKITE_API_SECRET={KITE_API_SECRET}\n'
        
        env_file.write_text(content)
        print("[OK] Saved to api_key.env")
        print("  - KITE_ACCESS_TOKEN updated")
        print("  - KITE_API_SECRET saved")
    else:
        print("Manually add to api_key.env:")
        print(f"KITE_ACCESS_TOKEN={access_token}")
        print(f"KITE_API_SECRET={KITE_API_SECRET}")
    
    print()
    print("Test connection: python test_kite_official.py")
    
except Exception as e:
    print()
    print(f"[ERROR] Failed: {e}")
    print()
    print("Possible causes:")
    print("1. Request token expired (get a fresh one)")
    print("2. API secret incorrect")
    print("3. Request token already used")
    sys.exit(1)

