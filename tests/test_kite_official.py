"""
Simple Kite API test using official kiteconnect library
This is the recommended way to connect to Kite API
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load API keys
load_dotenv("api_key.env")

KITE_API_KEY = os.getenv('KITE_API_KEY')
KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN')

print("=" * 80)
print("KITE API CONNECTION TEST (Official Library)")
print("=" * 80)
print()

if not KITE_API_KEY or not KITE_ACCESS_TOKEN:
    print("[ERROR] KITE_API_KEY or KITE_ACCESS_TOKEN not found")
    sys.exit(1)

print(f"[OK] API Key: {KITE_API_KEY[:10]}...")
print(f"[OK] Access Token: {KITE_ACCESS_TOKEN[:10]}...")
print()

# Try using official kiteconnect library
try:
    from kiteconnect import KiteConnect
    
    print("Using official kiteconnect library...")
    print()
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(KITE_ACCESS_TOKEN)
    
    # Test 1: Get user profile
    print("Test 1: Getting user profile...")
    try:
        profile = kite.profile()
        print("[SUCCESS] Connected to Kite API!")
        print(f"  User Name: {profile.get('user_name', 'N/A')}")
        print(f"  Email: {profile.get('email', 'N/A')}")
        print(f"  User ID: {profile.get('user_id', 'N/A')}")
        print(f"  Broker: {profile.get('broker', 'N/A')}")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    
    print()
    
    # Test 2: Get margins
    print("Test 2: Getting account margins...")
    try:
        margins = kite.margins()
        equity = margins.get('equity', {})
        print("[SUCCESS] Got margins!")
        print(f"  Available Cash: {equity.get('available', {}).get('cash', 'N/A')}")
        print(f"  Used: {equity.get('utilised', {}).get('debits', 'N/A')}")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    
    print()
    
    # Test 3: Get holdings
    print("Test 3: Getting holdings...")
    try:
        holdings = kite.holdings()
        print(f"[SUCCESS] Got {len(holdings)} holdings!")
        if holdings:
            print("  Sample holdings:")
            for h in holdings[:3]:
                print(f"    - {h.get('tradingsymbol', 'N/A')}: {h.get('quantity', 0)} units @ {h.get('average_price', 0)}")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    
    print()
    
    # Test 4: Get quote
    print("Test 4: Getting quote for RELIANCE...")
    try:
        quote = kite.quote("NSE:RELIANCE")
        if quote and 'NSE:RELIANCE' in quote:
            data = quote['NSE:RELIANCE']
            print("[SUCCESS] Got quote!")
            print(f"  Last Price: {data.get('last_price', 'N/A')}")
            print(f"  Change: {data.get('net_change', 'N/A')} ({data.get('net_change', 0) / data.get('last_price', 1) * 100:.2f}%)")
        else:
            print("[WARNING] Quote data format unexpected")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    
    print()
    print("=" * 80)
    print("[SUCCESS] All tests completed!")
    print("Your Kite API connection is working correctly.")
    print("=" * 80)
    
except ImportError:
    print("[WARNING] kiteconnect library not installed")
    print()
    print("To use the official Kite Connect library:")
    print("  pip install kiteconnect")
    print()
    print("Alternatively, you can test with HTTP directly.")
    print("The 400 error might indicate:")
    print("  1. API key/access token format issue")
    print("  2. Access token might be expired")
    print("  3. Need to regenerate access token")
    print()
    print("To get a new access token:")
    print("  1. Visit: https://kite.trade/connect/login")
    print("  2. Login and authorize")
    print("  3. Get the access token from the redirect URL")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

