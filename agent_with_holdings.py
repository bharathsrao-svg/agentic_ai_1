"""
Agentic AI app for stock holdings price variation analysis
Compares today's holdings (from Kite API) with yesterday's holdings (from JSON file)
and provides AI analysis on holdings with significant price movements
"""
from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from input_parsers.models import HoldingsData, StockHolding
from kite.kite_holdings import get_holdings_from_kite
from whatsapp.send_message import send_whatsapp_message_simple
from pathlib import Path
from datetime import datetime
import json
import argparse


def load_holdings_from_json(file_path: Path) -> HoldingsData:
    """
    Load holdings from JSON file (EOD holdings format)
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        HoldingsData object
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert JSON data back to StockHolding objects
    holdings = []
    for h in data.get('holdings', []):
        holding = StockHolding(
            symbol=h.get('symbol'),
            quantity=h.get('quantity'),
            price=h.get('price'),
            value=h.get('value'),
            company_name=h.get('company_name'),
            sector=h.get('sector'),
            exchange=h.get('exchange'),
            currency=h.get('currency'),
            date=datetime.fromisoformat(h['date']) if h.get('date') else None
        )
        holdings.append(holding)
    
    holdings_data = HoldingsData(
        holdings=holdings,
        source_file=data.get('source_file', str(file_path)),
        parse_date=datetime.fromisoformat(data['parse_date']) if data.get('parse_date') else datetime.now(),
        total_value=data.get('total_value')
    )
    
    return holdings_data


def get_holdings_by_symbol(holdings_data: HoldingsData) -> dict:
    """
    Create a dictionary mapping symbol (with exchange) to StockHolding
    
    Args:
        holdings_data: HoldingsData object
    
    Returns:
        Dictionary with key as "exchange:symbol" or "symbol" and value as StockHolding
    """
    holdings_dict = {}
    for holding in holdings_data.holdings:
        exchange = holding.exchange or ""
        key = f"{exchange}:{holding.symbol}" if exchange else holding.symbol
        holdings_dict[key] = holding
    return holdings_dict


def filter_holdings_by_price_variation(today_holdings: HoldingsData, 
                                       yesterday_holdings: HoldingsData,
                                       min_variation_percent: float = 5.0) -> HoldingsData:
    """
    Filter today's holdings to only include those with price variation > min_variation_percent
    compared to yesterday's holdings
    
    Args:
        today_holdings: Today's holdings from Kite API
        yesterday_holdings: Yesterday's holdings from JSON file
        min_variation_percent: Minimum price variation percentage (default: 5.0)
    
    Returns:
        HoldingsData object with filtered holdings
    """
    # Create lookup dictionaries
    today_dict = get_holdings_by_symbol(today_holdings)
    yesterday_dict = get_holdings_by_symbol(yesterday_holdings)
    
    filtered_holdings = []
    
    print(f"\nComparing holdings (min variation: {min_variation_percent}%)...")
    print("=" * 80)
    
    for key, today_holding in today_dict.items():
        if key in yesterday_dict:
            yesterday_holding = yesterday_dict[key]
            
            # Calculate price variation
            today_price = today_holding.price or 0
            yesterday_price = yesterday_holding.price or 0
            
            if yesterday_price > 0:
                variation_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # Check if variation exceeds threshold
                if abs(variation_percent) >= min_variation_percent:
                    # Create a new holding with variation info including yesterday's price and deviation
                    filtered_holding = StockHolding(
                        symbol=today_holding.symbol,
                        quantity=today_holding.quantity,
                        price=today_price,
                        value=today_holding.value,
                        company_name=today_holding.company_name,
                        sector=today_holding.sector,
                        exchange=today_holding.exchange,
                        currency=today_holding.currency,
                        date=today_holding.date,
                        yesterday_price=yesterday_price,
                        variation_percent=variation_percent
                    )
                    filtered_holdings.append(filtered_holding)
                    
                    direction = "UP" if variation_percent > 0 else "DOWN"
                    print(f"{direction:4} {today_holding.symbol:15} | "
                          f"Yesterday: Rs.{yesterday_price:10.2f} | "
                          f"Today: Rs.{today_price:10.2f} | "
                          f"Variation: {variation_percent:+.2f}%")
        else:
            # New holding (not in yesterday's data)
            # Could optionally include these as "new holdings"
            pass
    
    print("=" * 80)
    print(f"Found {len(filtered_holdings)} holdings with >{min_variation_percent}% price variation")
    
    # Calculate total value of filtered holdings
    total_value = sum(h.value or 0 for h in filtered_holdings)
    
    filtered_data = HoldingsData(
        holdings=filtered_holdings,
        source_file=f"Filtered holdings (>{min_variation_percent}% variation)",
        parse_date=datetime.now(),
        total_value=total_value
    )
    
    return filtered_data


# Removed unused functions: analyze_portfolio_with_ai and ask_question_about_holdings
# This script now focuses solely on price variation analysis


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Agentic AI app for stock holdings price variation analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare today's holdings with yesterday's (price variation >5%)
  python agent_with_holdings.py --date 20251124
  
  # Use custom variation threshold (e.g., 3%)
  python agent_with_holdings.py --date 20251124 --min-variation 3.0
        """
    )
    
    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help='Date in YYYYMMDD format for yesterday holdings file (e.g., 20251124). '
             'Used to compare with today holdings and filter by price variation >5%%'
    )
    parser.add_argument(
        '--min-variation',
        type=float,
        default=5.0,
        help='Minimum price variation percentage to filter (default: 5.0)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing EOD holdings JSON files (default: data)'
    )
    
    args = parser.parse_args()
    
    # Price variation analysis: Compare today's holdings with yesterday's
    if args.date:
        print("=" * 80)
        print("Price Variation Analysis")
        print("=" * 80)
        
        # Step 1: Get today's holdings from Kite API
        print("\n[Step 1] Fetching today's holdings from Kite API...")
        today_holdings = get_holdings_from_kite()
        print(f"Today's holdings: {len(today_holdings.holdings)} stocks")
        print(f"Total value: Rs. {today_holdings.total_value:,.2f}")
        
        # Step 2: Load yesterday's holdings from JSON file
        script_dir = Path(__file__).parent
        data_dir = script_dir / "data"
        yesterday_file = data_dir / f"eod_holdings_{args.date}.json"
        
        if not yesterday_file.exists():
            print(f"\n[ERROR] Yesterday's holdings file not found: {yesterday_file}")
            print("Please ensure the file exists or check the date format (YYYYMMDD)")
            exit(1)
        
        print(f"\n[Step 2] Loading yesterday's holdings from: {yesterday_file}")
        yesterday_holdings = load_holdings_from_json(yesterday_file)
        print(f"Yesterday's holdings: {len(yesterday_holdings.holdings)} stocks")
        print(f"Total value: Rs. {yesterday_holdings.total_value:,.2f}")
        
        # Step 3: Filter holdings with >5% price variation
        print(f"\n[Step 3] Filtering holdings with >{args.min_variation}% price variation...")
        filtered_holdings = filter_holdings_by_price_variation(
            today_holdings,
            yesterday_holdings,
            min_variation_percent=args.min_variation
        )
        
        if len(filtered_holdings.holdings) == 0:
            print(f"\nNo holdings found with >{args.min_variation}% price variation.")
        else:
            # Display filtered holdings
            print(f"\n{'='*80}")
            print(f"Filtered Holdings (> {args.min_variation}% variation)")
            print(f"{'='*80}")
            print(f"\nTotal filtered holdings: {len(filtered_holdings.holdings)}")
            print(f"Total value of filtered holdings: Rs. {filtered_holdings.total_value:,.2f}")
            
            # Display detailed table of filtered holdings with yesterday's price and variation
            if len(filtered_holdings.holdings) > 0:
                print(f"\n{'Symbol':<15} {'Yesterday':>12} {'Today':>12} {'Variation':>12} {'Quantity':>12} {'Value':>15}")
                print("-" * 80)
                for h in filtered_holdings.holdings:
                    direction = "UP" if h.variation_percent and h.variation_percent > 0 else "DOWN"
                    print(f"{h.symbol:<15} "
                          f"Rs.{h.yesterday_price:>10.2f} "
                          f"Rs.{h.price:>10.2f} "
                          f"{direction:4} {abs(h.variation_percent or 0):>9.2f}% "
                          f"{h.quantity:>12.0f} "
                          f"Rs.{h.value:>14,.2f}")
                print("-" * 80)
            
            # Step 4: Get AI analysis on filtered holdings
            print(f"\n[Step 4] Getting AI Analysis on filtered holdings...")
            print("=" * 80)
            
            # Prepare summary for AI (using filtered holdings)
            portfolio_summary = {
                "total_holdings": len(filtered_holdings.holdings),
                "total_value": filtered_holdings.total_value,
                "holdings": [
                    {
                        "symbol": h.symbol,
                        "company": h.company_name,
                        "quantity": h.quantity,
                        "price": h.price,
                        "value": h.value,
                        "sector": h.sector,
                        "yesterday_price": h.yesterday_price,
                        "variation_percent": h.variation_percent
                    }
                    for h in filtered_holdings.holdings
                ]
            }
            
            # Create prompt with filtered holdings data
            holdings_json = json.dumps(portfolio_summary, indent=2, default=str)
            print("\nFiltered Holdings Data:")
            print(holdings_json)
            
            template = """You are a financial advisor AI assistant analyzing stock price moves.
Please provide reasons why the stock prices of the attached holdings have moved significantly today compared to yesterday. The attached holdings has current price and yesterday's price.
For each question, respond ONLY with JSON formatted data in the template below bookmarked below by the keyword Response_Template :

Response_Template:            
{{
"hypotheses": [
    {{
    "description": "<reason description>",
    "confidence_score": 0.0-1.0,
    "event_date": "YYYY-MM-DD",
    "relevance_to_today": true or false,
    "source": "<type of source, e.g., news, financial report>"
    }},
    ...
],
"overall_confidence": 0.0-1.0,
"needs_follow_up": true or false,
"follow_up_question": "<optional follow-up question or empty>"
}}


Portfolio Data:
{holdings_data}


Answer in a clear, structured format."""

            prompt = PromptTemplate(
                input_variables=["holdings_data"],
                template=template
            )
            
            # Get AI analysis
            llm = ChatPerplexity(model="sonar", temperature=0.7)
            chain = LLMChain(llm=llm, prompt=prompt)
            
            print("\n" + "="*80)
            print("Getting AI Analysis...")
            print("="*80 + "\n")
            
            response = chain.run(holdings_data=holdings_json)
            print(response)
            
            # Send WhatsApp notification with filtered holdings count
            whatsapp_message = f"Found {len(filtered_holdings.holdings)} stocks with >{args.min_variation}% price variation"
            try:
                send_whatsapp_message_simple("919502757136", whatsapp_message)  # Replace with your phone number
            except Exception as e:
                print(f"[WARNING] Failed to send WhatsApp notification: {e}")
            