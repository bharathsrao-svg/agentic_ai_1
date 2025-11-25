"""
Enhanced Holdings Analyzer with Real-time Price Updates from MCP Kite Server
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List, Dict

from analyze_holdings_from_db import HoldingsAnalyzer
from input_parsers.db_persistence import HoldingsDBPersistence
from mcp_kite_client import KiteMCPClient, KiteMCPClientSync


class RealTimeHoldingsAnalyzer(HoldingsAnalyzer):
    """Enhanced analyzer with real-time price updates from Kite MCP"""
    
    def __init__(self, llm_model: str = "sonar", temperature: float = 0.7,
                 api_key_file: Optional[str] = None,
                 kite_api_key_file: Optional[str] = None,
                 use_realtime: bool = True):
        """
        Initialize analyzer with real-time price updates
        
        Args:
            llm_model: LLM model name
            temperature: LLM temperature
            api_key_file: Path to LLM API key file
            kite_api_key_file: Path to Kite API key file
            use_realtime: Whether to fetch real-time prices
        """
        super().__init__(llm_model, temperature, api_key_file)
        self.use_realtime = use_realtime
        self.kite_client = None
        
        if use_realtime:
            self.kite_client = KiteMCPClientSync(
                api_key_file=kite_api_key_file or api_key_file
            )
    
    def analyze_from_db_with_realtime(self, import_id: Optional[int] = None,
                                      source_file: Optional[str] = None,
                                      custom_query: Optional[str] = None) -> str:
        """
        Analyze holdings with real-time price updates
        
        Args:
            import_id: Specific import ID
            source_file: Source file name
            custom_query: Custom analysis query
            
        Returns:
            Analysis with real-time data
        """
        with HoldingsDBPersistence() as db:
            # Get holdings from database
            if import_id:
                holdings = db.get_holdings_by_import_id(import_id)
            elif source_file:
                imports = db.get_latest_imports(limit=100)
                matching = [imp for imp in imports if imp['source_file'] == source_file]
                if not matching:
                    return f"No imports found for file: {source_file}"
                holdings = db.get_holdings_by_import_id(matching[0]['id'])
            else:
                imports = db.get_latest_imports(limit=1)
                if not imports:
                    return "No holdings found in database."
                holdings = db.get_holdings_by_import_id(imports[0]['id'])
            
            if not holdings:
                return "No holdings found to analyze."
            
            # Update with real-time prices if enabled
            if self.use_realtime and self.kite_client:
                print("Fetching real-time prices from Kite...")
                try:
                    holdings = self.kite_client.update_holdings_with_prices(holdings)
                    print(f"Updated {len(holdings)} holdings with real-time prices")
                except Exception as e:
                    print(f"Warning: Could not fetch real-time prices: {e}")
                    print("Continuing with database prices...")
            
            # Format and analyze
            formatted_holdings = self.format_holdings_for_llm(holdings)
            
            # Enhanced query with real-time data context
            enhanced_query = custom_query or """Analyze this holdings file and share with me a consolidated file of analysis including:
1. 1 year returns for each holding (use current real-time prices if available)
2. My current holding value (using real-time prices)
3. Recommendation of whether I should buy or sell or retain this holding
4. Real-time price changes and market trends
5. P&L based on current prices vs purchase prices"""
            
            analysis = self.analyze_holdings(holdings, enhanced_query)
            return analysis


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze holdings with real-time price updates from Kite MCP'
    )
    parser.add_argument('--import-id', type=int, help='Analyze specific import ID')
    parser.add_argument('--source-file', type=str, help='Analyze specific source file')
    parser.add_argument('--config', default='input_parsers/db_config.env',
                       help='Database config file')
    parser.add_argument('--api-key-file', default='api_key.env',
                       help='LLM API key file')
    parser.add_argument('--kite-api-key-file', default='api_key.env',
                       help='Kite API key file')
    parser.add_argument('--no-realtime', action='store_true',
                       help='Disable real-time price updates')
    parser.add_argument('--output', type=str, help='Save analysis to file')
    
    args = parser.parse_args()
    
    # Load configs
    if Path(args.config).exists():
        load_dotenv(args.config)
    
    try:
        analyzer = RealTimeHoldingsAnalyzer(
            api_key_file=args.api_key_file,
            kite_api_key_file=args.kite_api_key_file,
            use_realtime=not args.no_realtime
        )
        
        print("=" * 80)
        print("REAL-TIME HOLDINGS ANALYSIS")
        print("=" * 80)
        print()
        
        analysis = analyzer.analyze_from_db_with_realtime(
            import_id=args.import_id,
            source_file=args.source_file
        )
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print()
        print(analysis)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(analysis)
            print(f"\nAnalysis saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

