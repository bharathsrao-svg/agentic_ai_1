"""
Example usage of the holdings parsers
"""
import json
import sys
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .parser_factory import HoldingsParserFactory
except ImportError:
    # If running as standalone script, import directly from module files
    import importlib.util
    
    # Get the directory containing this file
    parsers_dir = Path(__file__).parent
    
    # Load models first
    models_path = parsers_dir / "models.py"
    models_spec = importlib.util.spec_from_file_location("input_parsers.models", models_path)
    models_module = importlib.util.module_from_spec(models_spec)
    models_spec.loader.exec_module(models_module)
    sys.modules['input_parsers.models'] = models_module
    sys.modules['models'] = models_module  # Also register as 'models' for relative imports
    
    # Load excel_parser
    excel_parser_path = parsers_dir / "excel_parser.py"
    excel_spec = importlib.util.spec_from_file_location("input_parsers.excel_parser", excel_parser_path)
    excel_module = importlib.util.module_from_spec(excel_spec)
    excel_spec.loader.exec_module(excel_module)
    sys.modules['input_parsers.excel_parser'] = excel_module
    
    # Load pdf_parser
    pdf_parser_path = parsers_dir / "pdf_parser.py"
    pdf_spec = importlib.util.spec_from_file_location("input_parsers.pdf_parser", pdf_parser_path)
    pdf_module = importlib.util.module_from_spec(pdf_spec)
    pdf_spec.loader.exec_module(pdf_module)
    sys.modules['input_parsers.pdf_parser'] = pdf_module
    
    # Now load parser_factory
    parser_factory_path = parsers_dir / "parser_factory.py"
    factory_spec = importlib.util.spec_from_file_location("input_parsers.parser_factory", parser_factory_path)
    factory_module = importlib.util.module_from_spec(factory_spec)
    factory_spec.loader.exec_module(factory_module)
    sys.modules['input_parsers.parser_factory'] = factory_module
    
    HoldingsParserFactory = factory_module.HoldingsParserFactory


def parse_holdings_file(file_path: str):
    """Example function to parse a holdings file"""
    try:
        # Use factory to automatically select the right parser
        holdings_data = HoldingsParserFactory.parse_file(file_path)
        
        print(f"Successfully parsed {file_path}")
        print(f"Found {len(holdings_data.holdings)} holdings")
        print(f"Total value: {holdings_data.total_value}")
        print("\nHoldings:")
        print("-" * 80)
        
        for holding in holdings_data.holdings:
            print(f"Symbol: {holding.symbol}")
            if holding.company_name:
                print(f"  Company: {holding.company_name}")
            if holding.quantity:
                print(f"  Quantity: {holding.quantity}")
            if holding.price:
                print(f"  Price: {holding.price}")
            if holding.value:
                print(f"  Value: {holding.value}")
            if holding.sector:
                print(f"  Sector: {holding.sector}")
            print()
        
        # Export to JSON
        output_file = file_path.replace('.xlsx', '_parsed.json').replace('.xls', '_parsed.json').replace('.pdf', '_parsed.json')
        with open(output_file, 'w') as f:
            json.dump(holdings_data.to_dict(), f, indent=2)
        
        print(f"\nExported to: {output_file}")
        
        return holdings_data
        
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        parse_holdings_file(file_path)
    else:
        print("Usage: python example_usage.py <path_to_holdings_file>")
        print("Example: python example_usage.py holdings.xlsx")
        print("Example: python example_usage.py holdings.pdf")

