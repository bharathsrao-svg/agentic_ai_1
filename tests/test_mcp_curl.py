"""
Quick test script to show exact MCP request format
This demonstrates the exact URL and payload for get_holdings
"""
import json
import requests

# MCP Server URL (local)
MCP_URL = "http://localhost:8000/mcp"

# MCP Request for get_holdings
mcp_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_holdings",
        "arguments": {}
    }
}

print("=" * 80)
print("MCP REQUEST FOR get_holdings")
print("=" * 80)
print()
print(f"URL: {MCP_URL}")
print()
print("Method: POST")
print()
print("Headers:")
print("  Content-Type: application/json")
print()
print("Request Body:")
print(json.dumps(mcp_request, indent=2))
print()
print("=" * 80)
print("TESTING REQUEST")
print("=" * 80)
print()

try:
    response = requests.post(
        MCP_URL,
        json=mcp_request,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("Response:")
        print(json.dumps(result, indent=2)[:1000])  # First 1000 chars
        print()
        
        # Extract holdings from result
        if "result" in result and "content" in result["result"]:
            holdings = result["result"]["content"]
            print(f"[SUCCESS] Got {len(holdings)} holdings!")
            for h in holdings[:3]:
                print(f"  - {h.get('tradingsymbol', 'N/A')}: {h.get('quantity', 0)} units")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Could not connect to MCP server")
    print()
    print("Make sure the MCP server is running:")
    print("  python simple_mcp_server_example.py")
    print()
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 80)
print("cURL EQUIVALENT")
print("=" * 80)
print()
print("For Bash/Linux/Mac:")
print()
print(f"curl -X POST {MCP_URL} \\")
print("  -H 'Content-Type: application/json' \\")
print(f"  -d '{json.dumps(mcp_request)}'")
print()
print("For PowerShell (Windows):")
print()
print("# Using Invoke-WebRequest")
print("$body = @{")
print("    jsonrpc = '2.0'")
print("    id = 1")
print("    method = 'tools/call'")
print("    params = @{")
print("        name = 'get_holdings'")
print("        arguments = @{}")
print("    }")
print("} | ConvertTo-Json")
print()
print(f"Invoke-WebRequest -Uri '{MCP_URL}' -Method POST -ContentType 'application/json' -Body $body")
print()
print("# Or using curl.exe (if installed)")
print(f"curl.exe -X POST {MCP_URL} -H 'Content-Type: application/json' -d '{json.dumps(mcp_request).replace(chr(39), chr(92)+chr(34))}'")
print()

