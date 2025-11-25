"""
Script to fetch holdings from Kite API and save as EOD (End of Day) snapshot
Usage:
    python save_eod_holdings.py                    # Uses today's date (IST)
    python save_eod_holdings.py 20250115          # Uses specified date (YYYYMMDD)
    python save_eod_holdings.py 2025-01-15        # Also accepts YYYY-MM-DD format
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path for imports
script_dir = Path(__file__).parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from kite.kite_holdings import get_holdings_from_kite


def get_ist_date(date_str: str = None) -> str:
    """
    Get date string in YYYYMMDD format
    
    Args:
        date_str: Optional date string in YYYYMMDD or YYYY-MM-DD format
    
    Returns:
        Date string in YYYYMMDD format
    """
    if date_str:
        # Try to parse the date string
        try:
            # Try YYYYMMDD format first
            if len(date_str) == 8 and date_str.isdigit():
                date_obj = datetime.strptime(date_str, '%Y%m%d')
            # Try YYYY-MM-DD format
            elif len(date_str) == 10:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                raise ValueError(f"Invalid date format: {date_str}. Use YYYYMMDD or YYYY-MM-DD")
            
            return date_obj.strftime('%Y%m%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYYMMDD or YYYY-MM-DD. Error: {e}")
    else:
        # Use today's date in IST
        ist = pytz.timezone('Asia/Kolkata')
        today_ist = datetime.now(ist)
        return today_ist.strftime('%Y%m%d')


def save_holdings_to_file(holdings_data, output_dir: Path, date_str: str):
    """
    Save holdings data to JSON file
    
    Args:
        holdings_data: HoldingsData object
        output_dir: Directory to save the file
        date_str: Date string in YYYYMMDD format
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"eod_holdings_{date_str}.json"
    filepath = output_dir / filename
    
    # Convert holdings data to dictionary for JSON serialization
    holdings_dict = {
        "date": date_str,
        "source_file": holdings_data.source_file,
        "parse_date": holdings_data.parse_date.isoformat() if holdings_data.parse_date else None,
        "total_value": holdings_data.total_value,
        "total_holdings": len(holdings_data.holdings),
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "price": h.price,
                "value": h.value,
                "company_name": h.company_name,
                "sector": h.sector,
                "exchange": h.exchange,
                "currency": h.currency,
                "date": h.date.isoformat() if h.date else None
            }
            for h in holdings_data.holdings
        ]
    }
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(holdings_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Holdings saved to: {filepath}")
    print(f"Total holdings: {len(holdings_data.holdings)}")
    print(f"Total portfolio value: {holdings_data.total_value:,.2f}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Fetch holdings from Kite API and save as EOD snapshot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python save_eod_holdings.py                    # Uses today's date (IST)
  python save_eod_holdings.py 20250115           # Uses specified date (YYYYMMDD)
  python save_eod_holdings.py 2025-01-15         # Also accepts YYYY-MM-DD format
        """
    )
    parser.add_argument(
        'date',
        nargs='?',
        help='Date in YYYYMMDD or YYYY-MM-DD format (default: today in IST)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for holdings files (default: data)'
    )
    parser.add_argument(
        '--api-key-file',
        type=str,
        help='Path to API key file (default: api_key.env in parent directory)'
    )
    
    args = parser.parse_args()
    
    try:
        # Get date string
        date_str = get_ist_date(args.date)
        print(f"Using date: {date_str}")
        
        # Get output directory (script_dir already defined above)
        output_dir = script_dir / args.output_dir
        
        # Fetch holdings from Kite
        print("Fetching holdings from Kite API...")
        print("=" * 80)
        
        if args.api_key_file:
            holdings_data = get_holdings_from_kite(api_key_file=args.api_key_file)
        else:
            holdings_data = get_holdings_from_kite()
        
        print("=" * 80)
        
        # Save to file
        filepath = save_holdings_to_file(holdings_data, output_dir, date_str)
        
        print(f"\n[SUCCESS] EOD holdings snapshot saved successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to save EOD holdings: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

