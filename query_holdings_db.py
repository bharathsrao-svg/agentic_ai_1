"""
Script to query holdings data from PostgreSQL database
Usage: python query_holdings_db.py [options]
"""
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from input_parsers.db_persistence import HoldingsDBPersistence


def main():
    parser = argparse.ArgumentParser(description='Query holdings data from database')
    parser.add_argument('--config', help='Path to database config file (.env)', 
                       default='input_parsers/db_config.env')
    parser.add_argument('--import-id', type=int, help='Get holdings for specific import ID')
    parser.add_argument('--summary', action='store_true', help='Show database summary')
    parser.add_argument('--latest', type=int, default=5, 
                       help='Show latest N imports (default: 5)')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Load environment variables from config file if it exists
    config_path = Path(args.config)
    if config_path.exists():
        load_dotenv(config_path)
    
    try:
        with HoldingsDBPersistence() as db:
            if args.import_id:
                # Get holdings for specific import
                print(f"\nHoldings for Import ID: {args.import_id}")
                print("=" * 80)
                holdings = db.get_holdings_by_import_id(args.import_id)
                
                if args.format == 'json':
                    print(json.dumps(holdings, indent=2, default=str))
                else:
                    if holdings:
                        print(f"\n{'Symbol':<15} {'Company':<30} {'Quantity':<15} {'Price':<15} {'Value':<15}")
                        print("-" * 90)
                        for h in holdings:
                            print(f"{h['symbol']:<15} "
                                  f"{str(h['company_name'] or '')[:28]:<30} "
                                  f"{str(h['quantity'] or ''):<15} "
                                  f"{str(h['price'] or ''):<15} "
                                  f"{str(h['value'] or ''):<15}")
                    else:
                        print("No holdings found for this import ID")
            
            elif args.summary:
                # Show database summary
                print("\nDatabase Summary")
                print("=" * 80)
                summary = db.get_all_holdings_summary()
                
                if args.format == 'json':
                    print(json.dumps(summary, indent=2, default=str))
                else:
                    print(f"\nTotal Imports: {summary.get('total_imports', 0)}")
                    print(f"Total Holdings: {summary.get('total_holdings', 0)}")
                    print(f"Total Portfolio Value: {summary.get('total_portfolio_value', 0):,.2f}")
                    print(f"Unique Symbols: {summary.get('unique_symbols', 0)}")
                    print(f"Unique Sectors: {summary.get('unique_sectors', 0)}")
                    
                    if summary.get('top_holdings'):
                        print("\nTop 10 Holdings by Value:")
                        print("-" * 80)
                        print(f"{'Symbol':<15} {'Company':<30} {'Total Value':<20} {'Occurrences':<15}")
                        print("-" * 80)
                        for h in summary['top_holdings']:
                            print(f"{h['symbol']:<15} "
                                  f"{str(h['company_name'] or '')[:28]:<30} "
                                  f"{h['total_value']:>15,.2f} "
                                  f"{h['occurrence_count']:>15}")
            
            else:
                # Show latest imports
                print(f"\nLatest {args.latest} Imports")
                print("=" * 80)
                imports = db.get_latest_imports(args.latest)
                
                if args.format == 'json':
                    print(json.dumps(imports, indent=2, default=str))
                else:
                    if imports:
                        print(f"\n{'ID':<8} {'Source File':<40} {'Parse Date':<20} {'Total Value':<15} {'Holdings':<10}")
                        print("-" * 100)
                        for imp in imports:
                            print(f"{imp['id']:<8} "
                                  f"{str(imp['source_file'])[:38]:<40} "
                                  f"{str(imp['parse_date']):<20} "
                                  f"{str(imp['total_value'] or ''):<15} "
                                  f"{imp['total_holdings']:<10}")
                    else:
                        print("No imports found in database")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

