"""
MCP Client for connecting to mcp.kite.trade
Gets real-time stock prices and holdings updates
"""
import asyncio
import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not installed. Install with: pip install httpx")

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False
    # Warning suppressed - we use direct Kite API anyway, which is more reliable


class KiteMCPClient:
    """Client for connecting to mcp.kite.trade MCP server or direct Kite API"""
    
    def __init__(self, server_url: str = "https://mcp.kite.trade", 
                 api_key: Optional[str] = None,
                 access_token: Optional[str] = None,
                 api_key_file: Optional[str] = None,
                 use_direct_api: bool = True):
        """
        Initialize MCP client for Kite
        
        Args:
            server_url: MCP server URL (default: https://mcp.kite.trade)
            api_key: Kite API key (optional, can load from file)
            access_token: Kite access token (optional, can load from file)
            api_key_file: Path to API key file (optional)
            use_direct_api: If True, use direct Kite API instead of MCP server
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.access_token = access_token
        self.session = None
        self.use_direct_api = use_direct_api
        self.kite = None  # Direct Kite API client
        
        # Load API key from file if provided
        if api_key_file:
            api_key_path = Path(api_key_file)
            # If relative path, try parent directory (for files in subdirectories)
            if not api_key_path.exists() and not api_key_path.is_absolute():
                # Try parent directory
                parent_path = Path(__file__).parent.parent / api_key_path
                if parent_path.exists():
                    api_key_path = parent_path
            if api_key_path.exists():
                load_dotenv(api_key_path)
                self.api_key = self.api_key or os.getenv('KITE_API_KEY')
                self.access_token = self.access_token or os.getenv('KITE_ACCESS_TOKEN')
        
        # Try to get from environment if not set
        if not self.api_key:
            self.api_key = os.getenv('KITE_API_KEY')
        if not self.access_token:
            self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        
        # Initialize direct Kite API if enabled
        if self.use_direct_api and self.api_key and self.access_token:
            try:
                from kiteconnect import KiteConnect
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
            except ImportError:
                print("Warning: kiteconnect not installed. Install with: pip install kiteconnect")
    
    async def connect(self):
        """Connect to MCP server"""
        if HTTPX_AVAILABLE:
            self.session = httpx.AsyncClient(
                base_url=self.server_url,
                timeout=30.0,
                headers={
                    'Authorization': f'Bearer {self.api_key}' if self.api_key else None,
                    'Content-Type': 'application/json'
                }
            )
            print(f"Connected to MCP server at {self.server_url}")
        else:
            raise ImportError("httpx is required. Install with: pip install httpx")
    
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Call an MCP tool
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool response
        """
        if not self.session:
            await self.connect()
        
        # MCP tool call format
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.session.post("/mcp", json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            
            return result.get("result", {})
        except Exception as e:
            # Fallback: try direct HTTP endpoint
            return await self._http_fallback(tool_name, arguments)
    
    async def _http_fallback(self, tool_name: str, arguments: Dict) -> Dict:
        """Fallback HTTP method if MCP protocol fails"""
        try:
            # Use MCP endpoint, not direct tool endpoint
            endpoint = f"{self.server_url}/mcp"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            response = await self.session.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            return result.get("result", {})
        except Exception as e:
            raise Exception(f"Failed to call {tool_name}: {str(e)}")
    
    async def get_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS' or 'NSE:RELIANCE')
            
        Returns:
            Quote data with current price, etc.
        """
        # Use direct API if available
        if self.use_direct_api and self.kite:
            try:
                # Convert symbol to Kite format if needed
                if ':' not in symbol:
                    symbol = f"NSE:{symbol}"
                quotes = self.kite.quote(symbol)
                return quotes.get(symbol, {}) if quotes else {}
            except Exception as e:
                print(f"Direct API failed, trying MCP: {e}")
        
        return await self.call_tool("get_quote", {"symbol": symbol})
    
    async def get_quotes(self, symbols: List[str]) -> Dict:
        """
        Get real-time quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary of quotes keyed by symbol
        """
        return await self.call_tool("get_quotes", {"symbols": symbols})
    
    async def get_holdings(self) -> List[Dict]:
        """
        Get current holdings from Kite
        
        Returns:
            List of holdings with real-time prices
        """
        # Use direct API if available
        if self.use_direct_api and self.kite:
            try:
                return self.kite.holdings()
            except Exception as e:
                print(f"Direct API failed, trying MCP: {e}")
        
        return await self.call_tool("get_holdings", {})
    
    async def get_positions(self) -> List[Dict]:
        """
        Get current positions from Kite
        
        Returns:
            List of positions
        """
        return await self.call_tool("get_positions", {})
    
    async def get_margins(self) -> Dict:
        """
        Get account margins
        
        Returns:
            Margin information
        """
        return await self.call_tool("get_margins", {})
    
    async def update_holdings_with_prices(self, holdings: List[Dict]) -> List[Dict]:
        """
        Update holdings list with real-time prices from Kite
        
        Args:
            holdings: List of holdings from database
            
        Returns:
            Holdings with updated real-time prices
        """
        # Extract symbols from holdings
        symbols = []
        symbol_map = {}  # Map symbol to holding index
        
        for i, holding in enumerate(holdings):
            symbol = holding.get('symbol', '').strip()
            if symbol:
                # Convert to Kite format if needed (e.g., add exchange)
                kite_symbol = self._convert_to_kite_symbol(symbol)
                symbols.append(kite_symbol)
                symbol_map[kite_symbol] = i
        
        if not symbols:
            return holdings
        
        # Get real-time quotes
        try:
            quotes = await self.get_quotes(symbols)
            
            # Update holdings with real-time data
            updated_holdings = holdings.copy()
            for kite_symbol, quote_data in quotes.items():
                if kite_symbol in symbol_map:
                    idx = symbol_map[kite_symbol]
                    holding = updated_holdings[idx]
                    
                    # Update with real-time price
                    if 'last_price' in quote_data:
                        holding['current_price'] = quote_data['last_price']
                        # Recalculate value if quantity available
                        if holding.get('quantity'):
                            holding['current_value'] = holding['quantity'] * quote_data['last_price']
                    
                    # Add additional market data
                    holding['market_data'] = {
                        'open': quote_data.get('open'),
                        'high': quote_data.get('high'),
                        'low': quote_data.get('low'),
                        'close': quote_data.get('close'),
                        'volume': quote_data.get('volume'),
                        'change': quote_data.get('net_change'),
                        'change_percent': quote_data.get('net_change_percent')
                    }
            
            return updated_holdings
            
        except Exception as e:
            print(f"Warning: Could not fetch real-time prices: {e}")
            return holdings
    
    def _convert_to_kite_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Kite format
        Kite uses format: EXCHANGE:SYMBOL (e.g., NSE:RELIANCE)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Kite-formatted symbol
        """
        # If already in Kite format, return as is
        if ':' in symbol:
            return symbol
        
        # Default to NSE for Indian stocks
        # You may need to adjust based on your symbols
        return f"NSE:{symbol}"


# Synchronous wrapper for easier use
class KiteMCPClientSync:
    """Synchronous wrapper for KiteMCPClient"""
    
    def __init__(self, server_url: str = "https://mcp.kite.trade",
                 api_key: Optional[str] = None,
                 access_token: Optional[str] = None,
                 api_key_file: Optional[str] = None,
                 use_direct_api: bool = True):
        self.client = KiteMCPClient(server_url, api_key, access_token, api_key_file, use_direct_api)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote (synchronous)"""
        return self._get_loop().run_until_complete(
            self.client.get_quote(symbol)
        )
    
    def get_quotes(self, symbols: List[str]) -> Dict:
        """Get real-time quotes (synchronous)"""
        return self._get_loop().run_until_complete(
            self.client.get_quotes(symbols)
        )
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings (synchronous)"""
        return self._get_loop().run_until_complete(
            self.client.get_holdings()
        )
    
    def update_holdings_with_prices(self, holdings: List[Dict]) -> List[Dict]:
        """Update holdings with prices (synchronous)"""
        return self._get_loop().run_until_complete(
            self.client.update_holdings_with_prices(holdings)
        )


# Example usage
if __name__ == "__main__":
    async def main():
        # Async usage
        async with KiteMCPClient(api_key_file="api_key.env") as client:
            # Get quote for a symbol
            quote = await client.get_quote("RELIANCE")
            print(f"RELIANCE Quote: {quote}")
            
            # Get holdings
            holdings = await client.get_holdings()
            print(f"Holdings: {holdings}")
    
    # Sync usage
    def sync_example():
        client = KiteMCPClientSync(api_key_file="api_key.env")
        quote = client.get_quote("RELIANCE")
        print(f"RELIANCE Quote: {quote}")
    
    # Run async example
    asyncio.run(main())

