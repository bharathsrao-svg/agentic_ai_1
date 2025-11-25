"""
Simple Kite API call example - Get Holdings
This is a basic example to test your Kite API connection
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# Load API keys from api_key.env in parent directory
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
api_key_path = parent_dir / "api_key.env"
load_dotenv(api_key_path)

KITE_API_KEY = os.getenv('KITE_API_KEY')
KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN')

if not KITE_API_KEY or not KITE_ACCESS_TOKEN:
    print("[ERROR] KITE_API_KEY or KITE_ACCESS_TOKEN not found in api_key.env")
    exit(1)

print("=" * 80)
print("KITE API - GET HOLDINGS")
print("=" * 80)
print()

# Initialize Kite Connect
kite = KiteConnect(api_key=KITE_API_KEY)
kite.set_access_token(KITE_ACCESS_TOKEN)

try:
    # Test 1: Get user profile
    print("1. Getting user profile...")
    profile = kite.profile()
    print(f"   [OK] User: {profile.get('user_name', 'N/A')}")
    print(f"   [OK] Email: {profile.get('email', 'N/A')}")
    print()
    
    # Test 2: Get holdings
    print("2. Getting holdings...")
    holdings = kite.holdings()
    print(f"   [OK] Found {len(holdings)} holdings")
    print()
    
    if holdings:
        print("Holdings Details:")
        print("-" * 80)
        total_value = 0
        
        for i, holding in enumerate(holdings, 1):
            symbol = holding.get('tradingsymbol', 'N/A')
            quantity = holding.get('quantity', 0)
            avg_price = holding.get('average_price', 0)
            ltp = holding.get('last_price', 0)
            current_value = quantity * ltp if ltp else 0
            total_value += current_value
            
            pnl = (ltp - avg_price) * quantity if ltp and avg_price else 0
            pnl_percent = ((ltp - avg_price) / avg_price * 100) if avg_price else 0
            
            print(f"\n{i}. {symbol}")
            print(f"   Exchange: {holding.get('exchange', 'N/A')}")
            print(f"   Quantity: {quantity}")
            print(f"   Average Price: {avg_price:.2f}")
            print(f"   Last Price: {ltp:.2f}")
            print(f"   Current Value: {current_value:,.2f}")
            print(f"   P&L: {pnl:,.2f} ({pnl_percent:+.2f}%)")
        
        print()
        print("-" * 80)
        print(f"Total Portfolio Value: {total_value:,.2f}")
        print("=" * 80)
    else:
        print("   No holdings found")
    
    print()
    
    # Test 3: Get quote for a symbol
    print("3. Getting quote for RELIANCE...")
    quote = kite.quote("NSE:RELIANCE")
    if quote and 'NSE:RELIANCE' in quote:
        data = quote['NSE:RELIANCE']
        print(f"   [OK] Last Price: {data.get('last_price', 'N/A')}")
        print(f"   [OK] Change: {data.get('net_change', 'N/A')} ({data.get('net_change', 0) / data.get('last_price', 1) * 100:.2f}%)")
    else:
        print("   [WARNING] Could not get quote")
    
    print()
    print("=" * 80)
    print("[SUCCESS] All API calls completed successfully!")
    print("Your Kite API connection is working correctly.")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] API call failed: {e}")
    print()
    print("Possible issues:")
    print("1. Access token expired (regenerate using quick_generate_token.py)")
    print("2. Invalid API key or access token")
    print("3. Network connectivity issue")
    import traceback
    traceback.print_exc()

