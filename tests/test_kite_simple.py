"""
Simple Kite API connection test
Tests connection using official Kite Connect API
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
print("KITE API CONNECTION TEST")
print("=" * 80)
print()

if not KITE_API_KEY or not KITE_ACCESS_TOKEN:
    print("[ERROR] KITE_API_KEY or KITE_ACCESS_TOKEN not found")
    print("Make sure they are set in api_key.env")
    sys.exit(1)

print(f"[OK] API Key: {KITE_API_KEY[:10]}...")
print(f"[OK] Access Token: {KITE_ACCESS_TOKEN[:10]}...")
print()

# Test using httpx
try:
    import httpx
    
    print("Testing Kite Connect API...")
    print()
    
    # Kite Connect API base URL
    base_url = "https://kite.zerodha.com"
    
    # Create headers with authentication
    # Note: Direct HTTP calls to Kite API require proper authentication
    # The official library handles this better, but we'll try the standard format
    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}'
    }
    
    # Debug: Show what we're sending
    print(f"[DEBUG] Using API Key: {KITE_API_KEY[:10]}...")
    print(f"[DEBUG] Using Access Token: {KITE_ACCESS_TOKEN[:10]}...")
    print()
    
    with httpx.Client(timeout=10.0) as client:
        # Test 1: Get user profile
        print("Test 1: Getting user profile...")
        try:
            response = client.get(
                f"{base_url}/oms/user/profile",
                headers=headers
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    user_data = data.get('data', {})
                    print("[SUCCESS] Connected to Kite API!")
                    print(f"  User Name: {user_data.get('user_name', 'N/A')}")
                    print(f"  Email: {user_data.get('email', 'N/A')}")
                    print(f"  Broker: {user_data.get('broker', 'N/A')}")
                    print(f"  User ID: {user_data.get('user_id', 'N/A')}")
                else:
                    print(f"[ERROR] API returned error: {data.get('message', 'Unknown error')}")
            elif response.status_code == 401:
                print("[ERROR] Authentication failed")
                print("  Check if your API key and access token are correct")
                print(f"  Response: {response.text[:200]}")
            else:
                print(f"[ERROR] Request failed")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        print()
        
        # Test 2: Get margins
        print("Test 2: Getting account margins...")
        try:
            response = client.get(
                f"{base_url}/oms/user/margins",
                headers=headers
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    margins = data.get('data', {})
                    print("[SUCCESS] Got margins data!")
                    equity = margins.get('equity', {})
                    print(f"  Available: {equity.get('available', {}).get('cash', 'N/A')}")
                    print(f"  Used: {equity.get('utilised', {}).get('debits', 'N/A')}")
                else:
                    print(f"[WARNING] {data.get('message', 'Unknown response')}")
            else:
                print(f"[WARNING] Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
        
        print()
        
        # Test 3: Get holdings
        print("Test 3: Getting holdings...")
        try:
            response = client.get(
                f"{base_url}/oms/portfolio/holdings",
                headers=headers
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    holdings = data.get('data', [])
                    print(f"[SUCCESS] Got {len(holdings)} holdings!")
                    if holdings:
                        print("  Sample holdings:")
                        for h in holdings[:3]:  # Show first 3
                            print(f"    - {h.get('tradingsymbol', 'N/A')}: {h.get('quantity', 0)} units")
                else:
                    print(f"[WARNING] {data.get('message', 'Unknown response')}")
            else:
                print(f"[WARNING] Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
        
        print()
        
        # Test 4: Get quote for a symbol
        print("Test 4: Getting quote for RELIANCE...")
        try:
            # Kite uses instrument token or exchange:symbol format
            response = client.get(
                f"{base_url}/oms/quote",
                headers=headers,
                params={'i': 'NSE:RELIANCE'}  # NSE:SYMBOL format
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    quote_data = data.get('data', {}).get('NSE:RELIANCE', {})
                    if quote_data:
                        print("[SUCCESS] Got quote!")
                        print(f"  Last Price: {quote_data.get('last_price', 'N/A')}")
                        print(f"  Change: {quote_data.get('net_change', 'N/A')}")
                else:
                    print(f"[WARNING] {data.get('message', 'Unknown response')}")
            else:
                print(f"[WARNING] Status {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
except ImportError:
    print("[ERROR] httpx not installed")
    print("Install with: pip install httpx")
    sys.exit(1)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("If you see [SUCCESS] messages above, your Kite API connection is working!")
print()
print("Note: If all tests fail, verify:")
print("  1. API key and access token are correct and active")
print("  2. You have internet connectivity")
print("  3. Your Kite account has API access enabled")

