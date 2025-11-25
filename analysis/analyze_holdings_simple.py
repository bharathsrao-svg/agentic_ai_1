"""
Simple script to analyze holdings from database
Usage: python analyze_holdings_simple.py
"""
from pathlib import Path
from dotenv import load_dotenv
from analyze_holdings_from_db import HoldingsAnalyzer
from input_parsers.db_persistence import HoldingsDBPersistence

# Load database config
config_path = Path("input_parsers/db_config.env")
if config_path.exists():
    load_dotenv(config_path)

# Load API key from file
api_key_path = Path("api_key.env")
if api_key_path.exists():
    load_dotenv(api_key_path)
    print(f"Loaded API key from: {api_key_path}")
else:
    print(f"Warning: API key file not found: {api_key_path}")
    print("Make sure PPLX_API_KEY is set in environment or api_key.env file")

# Default analysis query
DEFAULT_QUERY = """Analyze this holdings file and share with me a consolidated file of analysis including:
1. 1 year returns for each holding
2. My holding value
3. Recommendation of whether I should buy or sell or retain this holding"""

def main():
    print("=" * 80)
    print("HOLDINGS ANALYSIS FROM DATABASE")
    print("=" * 80)
    print()
    
    # Initialize analyzer (will load API key from api_key.env by default)
    analyzer = HoldingsAnalyzer(api_key_file="api_key.env")
    
    # Analyze latest holdings from database
    analysis = analyzer.analyze_from_db(custom_query=DEFAULT_QUERY)
    
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()
    print(analysis)
    
    # Optionally save to file
    output_file = "holdings_analysis.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(analysis)
    print(f"\nAnalysis saved to: {output_file}")

if __name__ == "__main__":
    main()

