"""
Simple script to get holdings from Kite API
Usage: python get_kite_holdings.py
"""
import os
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from pathlib import Path

# Load credentials
# Load API keys from api_key.env in parent directory
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
api_key_path = parent_dir / "api_key.env"
load_dotenv(api_key_path)

kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))

# Get holdings
holdings = kite.holdings()

print(f"Found {len(holdings)} holdings:\n")

for h in holdings:
    symbol = h.get('tradingsymbol', 'N/A')
    qty = h.get('quantity', 0)
    ltp = h.get('last_price', 0)
    value = qty * ltp
    
    print(f"{symbol}: {qty} units @ {ltp} = {value:,.2f}")

