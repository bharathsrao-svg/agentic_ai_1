"""
Different ways to use the holdings parser
Choose the method that best fits your use case
"""

# ============================================================================
# METHOD 1: Import and use programmatically (RECOMMENDED for AI apps)
# ============================================================================
from input_parsers.parser_factory import HoldingsParserFactory
from input_parsers.models import HoldingsData, StockHolding

def parse_holdings_programmatically(file_path: str):
    """Use parser in your Python code"""
    # Automatically detects file type and uses appropriate parser
    holdings_data = HoldingsParserFactory.parse_file(file_path)
    
    # Access the data
    print(f"Found {len(holdings_data.holdings)} holdings")
    print(f"Total value: {holdings_data.total_value}")
    
    # Iterate through holdings
    for holding in holdings_data.holdings:
        print(f"{holding.symbol}: {holding.value}")
    
    # Convert to dictionary for JSON/API responses
    data_dict = holdings_data.to_dict()
    
    return holdings_data


# ============================================================================
# METHOD 2: Use specific parser directly
# ============================================================================
from input_parsers.excel_parser import ExcelHoldingsParser
from input_parsers.pdf_parser import PDFHoldingsParser

def parse_with_specific_parser(file_path: str, file_type: str = "auto"):
    """Use a specific parser if you know the file type"""
    if file_type == "excel" or file_path.endswith(('.xlsx', '.xls', '.xlsm')):
        parser = ExcelHoldingsParser()
        holdings_data = parser.parse_excel(file_path)
    elif file_type == "pdf" or file_path.endswith('.pdf'):
        parser = PDFHoldingsParser()
        holdings_data = parser.parse_pdf(file_path)
    else:
        # Use factory for auto-detection
        holdings_data = HoldingsParserFactory.parse_file(file_path)
    
    return holdings_data


# ============================================================================
# METHOD 3: Integrate with your Agentic AI app
# ============================================================================
def integrate_with_ai_agent(file_path: str):
    """Example: Parse holdings and prepare for AI analysis"""
    # Parse the holdings
    holdings_data = HoldingsParserFactory.parse_file(file_path)
    
    # Prepare data for AI agent
    portfolio_summary = {
        "total_holdings": len(holdings_data.holdings),
        "total_value": holdings_data.total_value,
        "holdings_by_sector": {},
        "top_holdings": []
    }
    
    # Group by sector
    for holding in holdings_data.holdings:
        sector = holding.sector or "Unknown"
        if sector not in portfolio_summary["holdings_by_sector"]:
            portfolio_summary["holdings_by_sector"][sector] = 0
        portfolio_summary["holdings_by_sector"][sector] += holding.value or 0
    
    # Get top 5 holdings by value
    sorted_holdings = sorted(
        holdings_data.holdings,
        key=lambda h: h.value or 0,
        reverse=True
    )
    portfolio_summary["top_holdings"] = [
        {
            "symbol": h.symbol,
            "value": h.value,
            "percentage": (h.value / holdings_data.total_value * 100) if holdings_data.total_value else 0
        }
        for h in sorted_holdings[:5]
    ]
    
    return holdings_data, portfolio_summary


# ============================================================================
# METHOD 4: Use in a function that can be called from your agent
# ============================================================================
def analyze_holdings(file_path: str) -> dict:
    """
    Parse and analyze holdings - can be called by your AI agent
    Returns a structured dictionary for analysis
    """
    try:
        holdings_data = HoldingsParserFactory.parse_file(file_path)
        
        analysis = {
            "status": "success",
            "source_file": holdings_data.source_file,
            "parse_date": holdings_data.parse_date.isoformat(),
            "summary": {
                "total_holdings": len(holdings_data.holdings),
                "total_portfolio_value": holdings_data.total_value,
                "average_holding_value": holdings_data.total_value / len(holdings_data.holdings) if holdings_data.holdings else 0
            },
            "holdings": [h.to_dict() for h in holdings_data.holdings],
            "sector_distribution": {},
            "top_holdings": []
        }
        
        # Sector analysis
        for holding in holdings_data.holdings:
            sector = holding.sector or "Uncategorized"
            if sector not in analysis["sector_distribution"]:
                analysis["sector_distribution"][sector] = {"count": 0, "total_value": 0}
            analysis["sector_distribution"][sector]["count"] += 1
            analysis["sector_distribution"][sector]["total_value"] += holding.value or 0
        
        # Top holdings
        sorted_holdings = sorted(
            holdings_data.holdings,
            key=lambda h: h.value or 0,
            reverse=True
        )[:10]
        
        analysis["top_holdings"] = [h.to_dict() for h in sorted_holdings]
        
        return analysis
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# EXAMPLE: Using in your agent_1.py or similar
# ============================================================================
if __name__ == "__main__":
    # Example 1: Simple parsing
    print("=" * 80)
    print("Example 1: Simple parsing")
    print("=" * 80)
    # holdings = parse_holdings_programmatically("holdings.pdf")
    
    # Example 2: With analysis
    print("\n" + "=" * 80)
    print("Example 2: With analysis")
    print("=" * 80)
    # analysis = analyze_holdings("holdings.pdf")
    # print(analysis)
    
    # Example 3: Integration with AI agent
    print("\n" + "=" * 80)
    print("Example 3: Integration with AI agent")
    print("=" * 80)
    # holdings_data, summary = integrate_with_ai_agent("holdings.pdf")
    # print(summary)
    
    print("\nTo use, uncomment the examples above and provide a file path")

