"""
Test local MCP server
This tests the MCP server running locally

Usage:
    python test_mcp_local.py                    # Test get_holdings (default)
    python test_mcp_local.py get_holdings      # Test get_holdings
    python test_mcp_local.py get_quote RELIANCE # Test get_quote for RELIANCE
    python test_mcp_local.py get_profile       # Test get_profile
"""
import asyncio
import httpx
import json
import sys
from mcp_kite_client import KiteMCPClient

async def test_local_mcp_server(method: str = "get_holdings", symbol: str = None):
    """Test the local MCP server"""
    print("=" * 80)
    print("TESTING LOCAL MCP SERVER")
    print("=" * 80)
    print()
    print("Make sure simple_mcp_server_example.py is running:")
    print("  python simple_mcp_server_example.py")
    print()
    
    # Connect to local MCP server
    async with KiteMCPClient(
        server_url="http://localhost:8000",
        api_key_file="api_key.env",
        use_direct_api=False  # Force MCP
    ) as client:
        print(f"[OK] Connected to local MCP server at {client.server_url}")
        print()
        
        # Test based on method argument
        if method == "get_holdings":
            print("Test: Get holdings via MCP...")
            try:
                holdings = await client.get_holdings()
                print(f"[SUCCESS] Got {len(holdings)} holdings via MCP!")
                for h in holdings[:3]:
                    print(f"  - {h.get('tradingsymbol', 'N/A')}: {h.get('quantity', 0)} units")
                print()
            except Exception as e:
                print(f"[ERROR] {e}")
                print()
        
        elif method == "get_quote":
            if not symbol:
                symbol = "RELIANCE"
            print(f"Test: Get quote for {symbol} via MCP...")
            try:
                quote = await client.get_quote(symbol)
                print(f"[SUCCESS] Got quote via MCP!")
                if isinstance(quote, dict) and "content" in quote:
                    data = quote["content"]
                    print(f"  Symbol: {symbol}")
                    print(f"  Last Price: {data.get('last_price', 'N/A')}")
                    print(f"  Open: {data.get('open', 'N/A')}")
                    print(f"  High: {data.get('high', 'N/A')}")
                    print(f"  Low: {data.get('low', 'N/A')}")
                    print(f"  Close: {data.get('close', 'N/A')}")
                    print(f"  Change: {data.get('net_change', 'N/A')}")
                else:
                    print(f"  Quote: {quote}")
                print()
            except Exception as e:
                print(f"[ERROR] {e}")
                print()
        
        elif method == "get_profile":
            print("Test: Get profile via MCP...")
            try:
                profile = await client.call_tool("get_profile", {})
                print(f"[SUCCESS] Got profile via MCP!")
                if isinstance(profile, dict) and "content" in profile:
                    data = profile["content"]
                    print(f"  User: {data.get('user_name', 'N/A')}")
                    print(f"  Email: {data.get('email', 'N/A')}")
                else:
                    print(f"  Profile: {profile}")
                print()
            except Exception as e:
                print(f"[ERROR] {e}")
                print()
        
        # Show MCP protocol for the requested method
        print("MCP Protocol Example:")
        print("-" * 80)
        arguments = {}
        if method == "get_quote" and symbol:
            arguments = {"symbol": symbol}
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": arguments
            }
        }
        print("Request:")
        print(json.dumps(payload, indent=2))
        print()
        
        # Try direct HTTP call
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    "http://localhost:8000/mcp",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                print("Response:")
                if "result" in result:
                    if "content" in result["result"]:
                        content = result["result"]["content"]
                        if method == "get_holdings":
                            print(f"  Found {len(content)} holdings")
                        elif method == "get_quote":
                            print(f"  Last Price: {content.get('last_price', 'N/A')}")
                            print(f"  Change: {content.get('net_change', 'N/A')}")
                        elif method == "get_profile":
                            print(f"  User: {content.get('user_name', 'N/A')}")
                    else:
                        print(json.dumps(result["result"], indent=2)[:500])
                elif "error" in result:
                    print(f"  Error: {result['error']}")
                else:
                    print(json.dumps(result, indent=2)[:500])
                print()
        except Exception as e:
            print(f"[ERROR] Direct HTTP call failed: {e}")
            print("Make sure the MCP server is running!")
            print()


if __name__ == "__main__":
    # Parse command line arguments
    method = "get_holdings"
    symbol = None
    
    if len(sys.argv) > 1:
        method = sys.argv[1]
    if len(sys.argv) > 2:
        symbol = sys.argv[2]
    
    print()
    print("=" * 80)
    print(f"TESTING MCP: {method.upper()}")
    if symbol:
        print(f"Symbol: {symbol}")
    print("=" * 80)
    print()
    
    asyncio.run(test_local_mcp_server(method, symbol))
    
    print()
    print("=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    print()
    print("  python test_mcp_local.py                    # get_holdings (default)")
    print("  python test_mcp_local.py get_holdings       # get_holdings")
    print("  python test_mcp_local.py get_quote RELIANCE  # get_quote for RELIANCE")
    print("  python test_mcp_local.py get_quote HDFCBANK  # get_quote for HDFCBANK")
    print("  python test_mcp_local.py get_profile         # get_profile")
    print()

