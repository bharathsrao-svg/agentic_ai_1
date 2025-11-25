"""
Test script to demonstrate mcp_kite_client.py usage
Shows how to use the MCP client with your Kite API credentials
"""
import asyncio
from mcp_kite_client import KiteMCPClient, KiteMCPClientSync
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

load_dotenv("api_key.env")

# Option 1: Use MCP Client (if MCP server is available)
async def test_mcp_client_async():
    """Test async MCP client"""
    print("=" * 80)
    print("TESTING MCP CLIENT (Async)")
    print("=" * 80)
    print()
    
    try:
        async with KiteMCPClient(api_key_file="api_key.env") as client:
            print("1. Getting quote for RELIANCE...")
            quote = await client.get_quote("RELIANCE")
            print(f"   Quote: {quote}")
            print()
            
            print("2. Getting all holdings...")
            holdings = await client.get_holdings()
            print(f"   Found {len(holdings)} holdings")
            for h in holdings[:3]:  # Show first 3
                print(f"   - {h.get('tradingsymbol', 'N/A')}: {h.get('quantity', 0)} units")
            print()
            
    except Exception as e:
        print(f"[ERROR] MCP client failed: {e}")
        print("Falling back to direct Kite API...")
        print()
        return False
    
    return True


# Option 2: Use Direct Kite API (more reliable)
def test_direct_kite_api():
    """Test direct Kite API connection"""
    print("=" * 80)
    print("TESTING DIRECT KITE API")
    print("=" * 80)
    print()
    
    kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
    kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))
    
    try:
        # Get profile
        profile = kite.profile()
        print(f"1. User: {profile.get('user_name', 'N/A')}")
        print()
        
        # Get holdings
        print("2. Getting holdings...")
        holdings = kite.holdings()
        print(f"   Found {len(holdings)} holdings")
        print()
        
        total_value = 0
        for h in holdings:
            symbol = h.get('tradingsymbol', 'N/A')
            qty = h.get('quantity', 0)
            ltp = h.get('last_price', 0)
            value = qty * ltp
            total_value += value
            
            print(f"   {symbol}: {qty} units @ {ltp} = {value:,.2f}")
        
        print()
        print(f"   Total Portfolio Value: {total_value:,.2f}")
        print()
        
        # Get quote for a symbol
        print("3. Getting quote for RELIANCE...")
        try:
            quote = kite.quote("NSE:RELIANCE")
            if quote and 'NSE:RELIANCE' in quote:
                data = quote['NSE:RELIANCE']
                print(f"   Last Price: {data.get('last_price', 'N/A')}")
                print(f"   Change: {data.get('net_change', 'N/A')}")
            else:
                print("   [WARNING] Could not get quote (permission issue)")
        except Exception as e:
            print(f"   [WARNING] Quote API requires different permissions: {e}")
        
        print()
        print("=" * 80)
        print("[SUCCESS] Direct Kite API is working!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Direct API failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Option 3: Use Sync MCP Client
def test_mcp_client_sync():
    """Test synchronous MCP client"""
    print("=" * 80)
    print("TESTING MCP CLIENT (Sync)")
    print("=" * 80)
    print()
    
    try:
        client = KiteMCPClientSync(api_key_file="api_key.env")
        
        print("1. Getting quote for RELIANCE...")
        quote = client.get_quote("RELIANCE")
        print(f"   Quote: {quote}")
        print()
        
        print("2. Getting holdings...")
        holdings = client.get_holdings()
        print(f"   Found {len(holdings)} holdings")
        print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Sync MCP client failed: {e}")
        print("This is expected if MCP server is not available.")
        print("Use direct Kite API instead (see test_direct_kite_api).")
        print()
        return False


# Main execution
if __name__ == "__main__":
    print()
    print("KITE API CLIENT TEST")
    print("=" * 80)
    print()
    
    # Try MCP client first (if available)
    print("Attempting MCP client connection...")
    mcp_worked = asyncio.run(test_mcp_client_async())
    print()
    
    if not mcp_worked:
        # Fallback to direct API
        print("Using direct Kite API (recommended)...")
        print()
        test_direct_kite_api()
    else:
        print()
        print("MCP client is working! You can use either method.")
        print()
        print("For direct API (more reliable), use:")
        print("  test_direct_kite_api()")
    
    print()
    print("=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    print()
    print("1. Direct Kite API (Recommended):")
    print("   from kiteconnect import KiteConnect")
    print("   kite = KiteConnect(api_key='your_key')")
    print("   kite.set_access_token('your_token')")
    print("   holdings = kite.holdings()")
    print()
    print("2. MCP Client (Async):")
    print("   from mcp_kite_client import KiteMCPClient")
    print("   async with KiteMCPClient(api_key_file='api_key.env') as client:")
    print("       holdings = await client.get_holdings()")
    print()
    print("3. MCP Client (Sync):")
    print("   from mcp_kite_client import KiteMCPClientSync")
    print("   client = KiteMCPClientSync(api_key_file='api_key.env')")
    print("   holdings = client.get_holdings()")
    print()

