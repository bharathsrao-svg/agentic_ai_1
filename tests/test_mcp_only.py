"""
Test MCP (Model Context Protocol) explicitly
This script forces MCP usage and disables direct API fallback
"""
import asyncio
from mcp_kite_client import KiteMCPClient, KiteMCPClientSync
from dotenv import load_dotenv
import os

load_dotenv("api_key.env")

print("=" * 80)
print("MCP-ONLY TEST (Direct API Disabled)")
print("=" * 80)
print()
print("This test forces MCP usage to learn how MCP works.")
print("Note: MCP server at mcp.kite.trade may not be available.")
print()

# ============================================================================
# Test 1: Async MCP Client (MCP only, no direct API)
# ============================================================================
async def test_mcp_async_only():
    """Test async MCP client with direct API disabled"""
    print("=" * 80)
    print("TEST 1: Async MCP Client (use_direct_api=False)")
    print("=" * 80)
    print()
    
    try:
        # Force MCP only - disable direct API
        async with KiteMCPClient(
            api_key_file="api_key.env",
            use_direct_api=False  # <-- Force MCP only
        ) as client:
            print("[OK] Connected to MCP server")
            print(f"Server URL: {client.server_url}")
            print()
            
            # Try to get holdings via MCP
            print("Attempting to get holdings via MCP...")
            holdings = await client.get_holdings()
            print(f"[SUCCESS] Got {len(holdings)} holdings via MCP!")
            return True
            
    except Exception as e:
        print(f"[ERROR] MCP connection failed: {e}")
        print()
        print("This is expected if:")
        print("  1. MCP server at mcp.kite.trade is not available")
        print("  2. MCP server requires different authentication")
        print("  3. MCP server doesn't exist yet")
        return False


# ============================================================================
# Test 2: Sync MCP Client (MCP only)
# ============================================================================
def test_mcp_sync_only():
    """Test sync MCP client with direct API disabled"""
    print("=" * 80)
    print("TEST 2: Sync MCP Client (use_direct_api=False)")
    print("=" * 80)
    print()
    
    try:
        # Force MCP only
        client = KiteMCPClientSync(
            api_key_file="api_key.env",
            use_direct_api=False  # <-- Force MCP only
        )
        
        print("[OK] Created MCP sync client")
        print(f"Server URL: {client.client.server_url}")
        print()
        
        # Try to get holdings via MCP
        print("Attempting to get holdings via MCP...")
        holdings = client.get_holdings()
        print(f"[SUCCESS] Got {len(holdings)} holdings via MCP!")
        return True
        
    except Exception as e:
        print(f"[ERROR] MCP sync client failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Test 3: Inspect MCP Connection Details
# ============================================================================
async def inspect_mcp_connection():
    """Inspect what happens when connecting to MCP"""
    print("=" * 80)
    print("TEST 3: Inspect MCP Connection")
    print("=" * 80)
    print()
    
    client = KiteMCPClient(
        api_key_file="api_key.env",
        use_direct_api=False
    )
    
    print("Client Configuration:")
    print(f"  Server URL: {client.server_url}")
    print(f"  API Key: {client.api_key[:10]}..." if client.api_key else "  API Key: None")
    print(f"  Use Direct API: {client.use_direct_api}")
    print(f"  Has Kite Client: {client.kite is not None}")
    print()
    
    try:
        await client.connect()
        print("[OK] HTTP session created")
        print(f"  Session base URL: {client.session.base_url}")
        print(f"  Session headers: {list(client.session.headers.keys())}")
        print()
        
        # Try a simple MCP tool call
        print("Testing MCP tool call format...")
        print("MCP uses JSON-RPC 2.0 protocol")
        print()
        
        # Example MCP payload
        example_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_holdings",
                "arguments": {}
            }
        }
        
        print("Example MCP request payload:")
        import json
        print(json.dumps(example_payload, indent=2))
        print()
        
        # Try actual call
        print("Attempting actual MCP call...")
        result = await client.call_tool("get_holdings", {})
        print(f"[SUCCESS] MCP call succeeded: {result}")
        return True
        
    except Exception as e:
        print(f"[ERROR] MCP inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


# ============================================================================
# Test 4: Check MCP SDK Availability
# ============================================================================
def check_mcp_sdk():
    """Check if MCP SDK is installed"""
    print("=" * 80)
    print("TEST 4: Check MCP SDK Availability")
    print("=" * 80)
    print()
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        print("[OK] MCP SDK is installed!")
        print("  You can use native MCP protocol")
        return True
    except ImportError as e:
        print("[INFO] MCP SDK is not installed")
        print(f"  Error: {e}")
        print()
        print("To install MCP SDK:")
        print("  pip install mcp")
        print()
        print("Note: Even without SDK, HTTP-based MCP can work")
        return False


# ============================================================================
# Main
# ============================================================================
if __name__ == "__main__":
    print()
    print("MCP-ONLY TESTING")
    print("=" * 80)
    print()
    print("This script tests MCP (Model Context Protocol) explicitly")
    print("by disabling the direct API fallback.")
    print()
    
    # Check SDK first
    has_sdk = check_mcp_sdk()
    print()
    
    # Run tests
    print("Running MCP tests...")
    print()
    
    # Test 1: Async
    result1 = asyncio.run(test_mcp_async_only())
    print()
    
    # Test 2: Sync
    result2 = test_mcp_sync_only()
    print()
    
    # Test 3: Inspect
    result3 = asyncio.run(inspect_mcp_connection())
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"MCP SDK Available: {has_sdk}")
    print(f"Async MCP Test: {'PASSED' if result1 else 'FAILED'}")
    print(f"Sync MCP Test: {'PASSED' if result2 else 'FAILED'}")
    print(f"MCP Inspection: {'PASSED' if result3 else 'FAILED'}")
    print()
    
    if not (result1 or result2 or result3):
        print("MCP server appears to be unavailable.")
        print()
        print("Possible reasons:")
        print("  1. MCP server at mcp.kite.trade doesn't exist")
        print("  2. Server requires different authentication")
        print("  3. Server is down or not accessible")
        print()
        print("For learning MCP, you might want to:")
        print("  1. Set up your own MCP server")
        print("  2. Use a different MCP server")
        print("  3. Study MCP protocol documentation")
    print()

