"""
Simple MCP Server Example for Learning
This creates a minimal MCP server that wraps Kite API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

load_dotenv("api_key.env")

app = FastAPI(title="Simple MCP Server for Kite")

# Initialize Kite (this would be done once at startup)
kite = None

def init_kite():
    """Initialize Kite connection"""
    global kite
    kite = KiteConnect(api_key=os.getenv('KITE_API_KEY'))
    kite.set_access_token(os.getenv('KITE_ACCESS_TOKEN'))


# MCP Request/Response Models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int = 1
    method: str
    params: Dict[str, Any]


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Any = None
    error: Any = None


# MCP Endpoint
@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest) -> MCPResponse:
    """
    MCP endpoint that handles tool calls
    This is the core of MCP - a single endpoint that routes to different tools
    """
    if request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        try:
            # Route to appropriate tool
            if tool_name == "get_holdings":
                result = await get_holdings_tool(arguments)
            elif tool_name == "get_quote":
                result = await get_quote_tool(arguments)
            elif tool_name == "get_profile":
                result = await get_profile_tool(arguments)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                result={"content": result}
            )
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={"code": -1, "message": str(e)}
            )
    else:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={"code": -1, "message": f"Unknown method: {request.method}"}
        )


# MCP Tools (these are what MCP exposes)
async def get_holdings_tool(arguments: Dict) -> List[Dict]:
    """MCP tool: get_holdings"""
    if not kite:
        init_kite()
    return kite.holdings()


async def get_quote_tool(arguments: Dict) -> Dict:
    """MCP tool: get_quote"""
    if not kite:
        init_kite()
    symbol = arguments.get("symbol")
    if not symbol:
        raise ValueError("symbol argument required")
    
    # Convert to Kite format if needed
    if ':' not in symbol:
        symbol = f"NSE:{symbol}"
    
    quotes = kite.quote(symbol)
    return quotes.get(symbol, {})


async def get_profile_tool(arguments: Dict) -> Dict:
    """MCP tool: get_profile"""
    if not kite:
        init_kite()
    return kite.profile()


# Health check
@app.get("/")
async def root():
    return {"message": "Simple MCP Server for Kite", "status": "running"}


# List available tools (MCP discovery)
@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_holdings",
                "description": "Get all holdings from Kite",
                "arguments": {}
            },
            {
                "name": "get_quote",
                "description": "Get quote for a symbol",
                "arguments": {"symbol": "string"}
            },
            {
                "name": "get_profile",
                "description": "Get user profile",
                "arguments": {}
            }
        ]
    }


if __name__ == "__main__":
    print("=" * 80)
    print("SIMPLE MCP SERVER FOR LEARNING")
    print("=" * 80)
    print()
    print("This is a minimal MCP server that wraps Kite API")
    print("It demonstrates how MCP protocol works")
    print()
    print("Server will start at: http://localhost:8000")
    print()
    print("Test it with:")
    print("  curl -X POST http://localhost:8000/mcp \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"get_holdings\",\"arguments\":{}}}'")
    print()
    print("Or use test_mcp_local.py to test it")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

