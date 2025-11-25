"""
Simple script to test Kite API connection
Tests both direct Kite API and MCP server connection
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load API keys
api_key_file = Path("api_key.env")
if api_key_file.exists():
    load_dotenv(api_key_file)
    print(f"[OK] Loaded API keys from {api_key_file}")
else:
    print(f"[ERROR] API key file not found: {api_key_file}")
    sys.exit(1)

KITE_API_KEY = os.getenv('KITE_API_KEY')
KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN')

if not KITE_API_KEY:
    print("[ERROR] KITE_API_KEY not found in environment")
    sys.exit(1)

if not KITE_ACCESS_TOKEN:
    print("[ERROR] KITE_ACCESS_TOKEN not found in environment")
    sys.exit(1)

print(f"[OK] Found KITE_API_KEY: {KITE_API_KEY[:10]}...")
print(f"[OK] Found KITE_ACCESS_TOKEN: {KITE_ACCESS_TOKEN[:10]}...")
print()

# Test 1: Direct Kite API connection
print("=" * 80)
print("TEST 1: Direct Kite API Connection")
print("=" * 80)

try:
    import httpx
    
    # Kite API base URL
    kite_base_url = "https://kite.zerodha.com"
    
    # Test connection - Get user profile (requires authentication)
    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}'
    }
    
    print(f"Connecting to {kite_base_url}...")
    
    with httpx.Client(timeout=10.0) as client:
        # Try to get user profile
        try:
            response = client.get(
                f"{kite_base_url}/oms/user/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                profile = response.json()
                print("[SUCCESS] Connected to Kite API!")
                print(f"  User: {profile.get('data', {}).get('user_name', 'N/A')}")
                print(f"  Email: {profile.get('data', {}).get('email', 'N/A')}")
                print(f"  Broker: {profile.get('data', {}).get('broker', 'N/A')}")
            elif response.status_code == 401:
                print("[ERROR] Authentication failed - Check your API key and access token")
                print(f"  Response: {response.text}")
            else:
                print(f"[ERROR] Connection failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                
        except httpx.RequestError as e:
            print(f"[ERROR] Connection error: {e}")
            print("  Note: This might be a network issue or incorrect API endpoint")
    
except ImportError:
    print("[ERROR] httpx not installed. Install with: pip install httpx")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test 2: MCP Server connection (mcp.kite.trade)
print("=" * 80)
print("TEST 2: MCP Server Connection (mcp.kite.trade)")
print("=" * 80)

try:
    import httpx
    
    mcp_server_url = "https://mcp.kite.trade"
    
    print(f"Connecting to {mcp_server_url}...")
    
    with httpx.Client(timeout=10.0) as client:
        # Test MCP server connection
        try:
            # Try a simple health check or tool list
            response = client.get(
                f"{mcp_server_url}/health",
                timeout=5.0
            )
            
            if response.status_code == 200:
                print("[SUCCESS] MCP server is reachable!")
                print(f"  Response: {response.text[:200]}")
            else:
                print(f"[WARNING] Server responded with status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except httpx.ConnectError:
            print("[ERROR] Could not connect to MCP server")
            print("  This might mean:")
            print("  - Server is down")
            print("  - URL is incorrect")
            print("  - Network/firewall issue")
        except httpx.TimeoutException:
            print("[ERROR] Connection timeout")
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            
        # Try MCP tool call
        print("\nTrying MCP tool call...")
        try:
            mcp_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            response = client.post(
                f"{mcp_server_url}/mcp",
                json=mcp_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {KITE_ACCESS_TOKEN}'
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[SUCCESS] MCP server responded!")
                print(f"  Response: {json.dumps(result, indent=2)[:500]}")
            else:
                print(f"[WARNING] MCP call returned status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"[ERROR] MCP tool call failed: {e}")
    
except ImportError:
    print("[ERROR] httpx not installed. Install with: pip install httpx")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test 3: Using our MCP client
print("=" * 80)
print("TEST 3: Using MCP Kite Client")
print("=" * 80)

try:
    from mcp_kite_client import KiteMCPClientSync
    
    print("Initializing MCP client...")
    client = KiteMCPClientSync(api_key_file="api_key.env")
    
    print("Testing get_quote for RELIANCE...")
    try:
        quote = client.get_quote("RELIANCE")
        print("[SUCCESS] Got quote from MCP client!")
        print(f"  Quote data: {quote}")
    except Exception as e:
        print(f"[ERROR] Failed to get quote: {e}")
        print("  This might mean:")
        print("  - MCP server connection issue")
        print("  - Symbol format issue")
        print("  - Authentication problem")
    
except ImportError as e:
    print(f"[ERROR] Could not import MCP client: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("If any test shows [SUCCESS], your connection is working!")
print("If all tests fail, check:")
print("  1. API key and access token are correct")
print("  2. Network connectivity")
print("  3. Kite API service status")
print("  4. MCP server URL is correct (if using MCP)")

