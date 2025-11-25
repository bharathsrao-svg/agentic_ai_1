"""
Helper script to get Kite Access Token
Use this if you have the request_token from Kite Connect login
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# Load API key
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
api_key_path = parent_dir / "api_key.env"
load_dotenv(api_key_path)

KITE_API_KEY = os.getenv('KITE_API_KEY')
KITE_API_SECRET = os.getenv('KITE_API_SECRET')  # You need to add this to api_key.env

print("=" * 80)
print("KITE ACCESS TOKEN GENERATOR")
print("=" * 80)
print()

if not KITE_API_KEY:
    print("[ERROR] KITE_API_KEY not found in api_key.env")
    sys.exit(1)

if not KITE_API_SECRET:
    print("[WARNING] KITE_API_SECRET not found")
    print()
    print("To get API Secret:")
    print("1. Login to Kite: https://kite.trade")
    print("2. Go to Settings -> API (or developers.kite.trade)")
    print("3. Find your app and copy the API Secret")
    print("4. Add to api_key.env: KITE_API_SECRET=your_secret_here")
    print()
    print("Alternatively, you can enter it manually when prompted.")
    print()
    
    api_secret = input("Enter API Secret (or press Enter to exit): ").strip()
    if not api_secret:
        sys.exit(1)
    KITE_API_SECRET = api_secret

print(f"[OK] API Key: {KITE_API_KEY[:10]}...")
print()

# Get request token from user
print("To get request token:")
print("1. Visit: https://kite.trade/connect/login?api_key=" + KITE_API_KEY + "&v=3")
print("2. Login with your Kite credentials")
print("3. After login, you'll be redirected")
print("4. Copy the 'request_token' from the redirect URL")
print()
print("Example redirect URL:")
print("  https://your-url.com/?request_token=XXXXX&action=login&status=success")
print()

request_token = input("Enter request_token from redirect URL: ").strip()

if not request_token:
    print("[ERROR] Request token is required")
    sys.exit(1)

try:
    print()
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
    print("Update your api_key.env file with:")
    print(f"KITE_ACCESS_TOKEN={access_token}")
    print()
    
    # Optionally update the file automatically
    update = input("Update api_key.env automatically? (y/n): ").strip().lower()
    if update == 'y':
        env_file = Path("api_key.env")
        if env_file.exists():
            content = env_file.read_text()
            # Replace or add KITE_ACCESS_TOKEN
            if 'KITE_ACCESS_TOKEN=' in content:
                import re
                content = re.sub(
                    r'KITE_ACCESS_TOKEN=.*',
                    f'KITE_ACCESS_TOKEN={access_token}',
                    content
                )
            else:
                content += f'\nKITE_ACCESS_TOKEN={access_token}\n'
            
            env_file.write_text(content)
            print("[OK] Updated api_key.env")
        else:
            print("[WARNING] api_key.env not found, please update manually")
    
    print()
    print("Test your connection with: python test_kite_official.py")
    
except Exception as e:
    print()
    print(f"[ERROR] Failed to generate access token: {e}")
    print()
    print("Common issues:")
    print("1. Request token expired (get a new one)")
    print("2. API secret is incorrect")
    print("3. App not enabled for your user (see KITE_API_SETUP_GUIDE.md)")
    sys.exit(1)

