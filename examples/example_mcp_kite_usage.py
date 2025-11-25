"""
Simple example showing how to use mcp_kite_client.py
This demonstrates the most common use cases
"""
import asyncio
from mcp_kite_client import KiteMCPClient, KiteMCPClientSync
from dotenv import load_dotenv

load_dotenv("api_key.env")

# ============================================================================
# EXAMPLE 1: Async Usage (Recommended for async code)
# ============================================================================
async def example_async_usage():
    """Example using async MCP client"""
    print("=" * 80)
    print("EXAMPLE 1: Async Usage")
    print("=" * 80)
    print()
    
    # Use context manager for automatic connection handling
    async with KiteMCPClient(api_key_file="api_key.env", use_direct_api=True) as client:
        # Get all holdings
        print("Getting holdings...")
        holdings = await client.get_holdings()
        
        print(f"Found {len(holdings)} holdings:\n")
        for h in holdings:
            symbol = h.get('tradingsymbol', 'N/A')
            qty = h.get('quantity', 0)
            ltp = h.get('last_price', 0)
            value = qty * ltp
            print(f"  {symbol}: {qty} units @ {ltp} = {value:,.2f}")
        
        print()


# ============================================================================
# EXAMPLE 2: Sync Usage (Easier for simple scripts)
# ============================================================================
def example_sync_usage():
    """Example using sync MCP client"""
    print("=" * 80)
    print("EXAMPLE 2: Sync Usage (Simplest)")
    print("=" * 80)
    print()
    
    # Create sync client
    client = KiteMCPClientSync(api_key_file="api_key.env", use_direct_api=True)
    
    # Get holdings (no await needed!)
    print("Getting holdings...")
    holdings = client.get_holdings()
    
    print(f"Found {len(holdings)} holdings:\n")
    total_value = 0
    for h in holdings:
        symbol = h.get('tradingsymbol', 'N/A')
        qty = h.get('quantity', 0)
        ltp = h.get('last_price', 0)
        value = qty * ltp
        total_value += value
        
        # Calculate P&L
        avg_price = h.get('average_price', 0)
        pnl = (ltp - avg_price) * qty if avg_price else 0
        pnl_pct = ((ltp - avg_price) / avg_price * 100) if avg_price else 0
        
        print(f"  {symbol}:")
        print(f"    Quantity: {qty}")
        print(f"    Avg Price: {avg_price:.2f}")
        print(f"    Last Price: {ltp:.2f}")
        print(f"    Current Value: {value:,.2f}")
        print(f"    P&L: {pnl:,.2f} ({pnl_pct:+.2f}%)")
        print()
    
    print(f"Total Portfolio Value: {total_value:,.2f}")
    print()


# ============================================================================
# EXAMPLE 3: Update Holdings with Real-time Prices
# ============================================================================
def example_update_holdings():
    """Example of updating holdings from database with real-time prices"""
    print("=" * 80)
    print("EXAMPLE 3: Update Holdings with Real-time Prices")
    print("=" * 80)
    print()
    
    # Simulate holdings from database (you'd get these from your DB)
    db_holdings = [
        {'symbol': 'BANKBEES', 'quantity': 1150, 'price': 554.37},
        {'symbol': 'HDFCBANK', 'quantity': 820, 'price': 877.03},
        {'symbol': 'SILVERBEES', 'quantity': 10820, 'price': 85.65},
    ]
    
    print("Holdings from database (with old prices):")
    for h in db_holdings:
        print(f"  {h['symbol']}: {h['quantity']} @ {h['price']}")
    print()
    
    # Update with real-time prices
    client = KiteMCPClientSync(api_key_file="api_key.env", use_direct_api=True)
    updated = client.update_holdings_with_prices(db_holdings)
    
    print("Holdings with real-time prices:")
    for h in updated:
        symbol = h.get('symbol', 'N/A')
        qty = h.get('quantity', 0)
        old_price = h.get('price', 0)
        current_price = h.get('current_price', old_price)
        value = qty * current_price
        
        print(f"  {symbol}: {qty} @ {current_price} = {value:,.2f}")
    print()


# ============================================================================
# EXAMPLE 4: Get Quote for Specific Symbol
# ============================================================================
async def example_get_quote():
    """Example of getting quote for a specific symbol"""
    print("=" * 80)
    print("EXAMPLE 4: Get Quote for Symbol")
    print("=" * 80)
    print()
    
    async with KiteMCPClient(api_key_file="api_key.env", use_direct_api=True) as client:
        # Try to get quote (may require additional permissions)
        try:
            quote = await client.get_quote("RELIANCE")
            print(f"RELIANCE Quote: {quote}")
        except Exception as e:
            print(f"Could not get quote (permission issue): {e}")
            print("Note: Quote API may require additional permissions in your Kite app")
    print()


# ============================================================================
# MAIN: Run Examples
# ============================================================================
if __name__ == "__main__":
    print()
    print("MCP KITE CLIENT - USAGE EXAMPLES")
    print("=" * 80)
    print()
    
    # Example 2 is simplest and most useful
    example_sync_usage()
    
    # Uncomment to try other examples:
    # asyncio.run(example_async_usage())
    # example_update_holdings()
    # asyncio.run(example_get_quote())
    
    print()
    print("=" * 80)
    print("QUICK REFERENCE")
    print("=" * 80)
    print()
    print("Simplest usage (sync):")
    print("  from mcp_kite_client import KiteMCPClientSync")
    print("  client = KiteMCPClientSync(api_key_file='api_key.env')")
    print("  holdings = client.get_holdings()")
    print()
    print("Async usage:")
    print("  from mcp_kite_client import KiteMCPClient")
    print("  async with KiteMCPClient(api_key_file='api_key.env') as client:")
    print("      holdings = await client.get_holdings()")
    print()

