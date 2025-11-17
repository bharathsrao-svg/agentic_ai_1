"""
Script to parse holdings files and save to PostgreSQL database
Usage: python save_holdings_to_db.py <file_path> [--config <config_file>]
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from input_parsers.parser_factory import HoldingsParserFactory
from input_parsers.db_persistence import HoldingsDBPersistence


def main():
    parser = argparse.ArgumentParser(description='Parse holdings file and save to database')
    parser.add_argument('file_path', help='Path to holdings file (Excel or PDF)')
    parser.add_argument('--config', help='Path to database config file (.env)', 
                       default='input_parsers/db_config.env')
    parser.add_argument('--create-tables', action='store_true',
                       help='Create database tables if they don\'t exist')
    parser.add_argument('--alter-tables', action='store_true',
                       help='Alter existing table columns to increase size (for existing databases)')
    parser.add_argument('--migrate-idempotent', action='store_true',
                       help='Migrate existing tables to support idempotent upserts')
    parser.add_argument('--host', help='Database host', default=None)
    parser.add_argument('--port', help='Database port', default=None)
    parser.add_argument('--database', help='Database name', default=None)
    parser.add_argument('--user', help='Database user', default=None)
    parser.add_argument('--password', help='Database password', default=None)
    
    args = parser.parse_args()
    
    # Load environment variables from config file if it exists
    config_path = Path(args.config)
    if config_path.exists():
        load_dotenv(config_path)
        print(f"Loaded configuration from {config_path}")
    else:
        # Try to load from example file as fallback
        example_path = Path(args.config).parent / "db_config.env.example"
        if example_path.exists():
            print(f"Warning: {config_path} not found. Trying {example_path}")
            load_dotenv(example_path)
        else:
            print(f"Config file not found: {config_path}")
            print("Using environment variables or defaults")
    
    # Build database config
    db_config = {}
    if args.host:
        db_config['host'] = args.host
    if args.port:
        db_config['port'] = args.port
    if args.database:
        db_config['database'] = args.database
    if args.user:
        db_config['user'] = args.user
    if args.password:
        db_config['password'] = args.password
    
    # Check if file exists
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        # Parse holdings file
        print(f"Parsing {file_path}...")
        holdings_data = HoldingsParserFactory.parse_file(file_path)
        print(f"Successfully parsed {len(holdings_data.holdings)} holdings")
        print(f"Total value: {holdings_data.total_value:,.2f}")
        
        # Save to database
        print("\nConnecting to database...")
        with HoldingsDBPersistence(db_config if db_config else None) as db:
            # Create tables if requested
            if args.create_tables:
                print("Creating database tables...")
                db.create_tables()
            
            # Migrate to idempotent schema if requested
            if args.migrate_idempotent:
                print("Migrating to idempotent schema...")
                db.migrate_to_idempotent()
            
            # Alter table columns if requested
            if args.alter_tables:
                print("Altering table columns...")
                db.alter_table_columns()
            
            # Save holdings (with upsert enabled by default)
            print("Saving holdings to database...")
            import_id = db.save_holdings(holdings_data)
            
            print(f"\n{'='*80}")
            print(f"Successfully saved holdings to database!")
            print(f"Import ID: {import_id}")
            print(f"Total holdings: {len(holdings_data.holdings)}")
            print(f"Total value: {holdings_data.total_value:,.2f}")
            print(f"{'='*80}")
            
            # Show summary
            print("\nDatabase Summary:")
            summary = db.get_all_holdings_summary()
            print(f"  Total imports: {summary.get('total_imports', 0)}")
            print(f"  Total holdings: {summary.get('total_holdings', 0)}")
            print(f"  Total portfolio value: {summary.get('total_portfolio_value', 0):,.2f}")
            print(f"  Unique symbols: {summary.get('unique_symbols', 0)}")
            print(f"  Unique sectors: {summary.get('unique_sectors', 0)}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

