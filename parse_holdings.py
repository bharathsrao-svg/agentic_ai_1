"""
Standalone script to parse stock holdings from Excel or PDF files
Usage: python parse_holdings.py <file_path>
"""
import sys
import json
from pathlib import Path
from input_parsers.parser_factory import HoldingsParserFactory


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_holdings.py <path_to_holdings_file>")
        print("\nSupported formats:")
        print("  - Excel: .xlsx, .xls, .xlsm")
        print("  - PDF: .pdf")
        print("\nExample:")
        print("  python parse_holdings.py holdings.xlsx")
        print("  python parse_holdings.py holdings.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        print(f"Parsing {file_path}...")
        holdings_data = HoldingsParserFactory.parse_file(file_path)
        
        print(f"\n{'='*80}")
        print(f"Successfully parsed: {file_path}")
        print(f"{'='*80}")
        print(f"Total holdings found: {len(holdings_data.holdings)}")
        if holdings_data.total_value:
            print(f"Total portfolio value: {holdings_data.total_value:,.2f}")
        print(f"\nHoldings Details:")
        print("-" * 80)
        
        for i, holding in enumerate(holdings_data.holdings, 1):
            print(f"\n{i}. {holding.symbol}")
            if holding.company_name:
                print(f"   Company: {holding.company_name}")
            if holding.quantity:
                print(f"   Quantity: {holding.quantity:,.2f}")
            if holding.price:
                print(f"   Price: {holding.price:.2f}")
            if holding.value:
                print(f"   Value: {holding.value:,.2f}")
            if holding.sector:
                print(f"   Sector: {holding.sector}")
            if holding.exchange:
                print(f"   Exchange: {holding.exchange}")
        
        # Export to JSON
        output_file = str(Path(file_path).stem) + "_parsed.json"
        with open(output_file, 'w') as f:
            json.dump(holdings_data.to_dict(), f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print(f"Exported parsed data to: {output_file}")
        print(f"{'='*80}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

