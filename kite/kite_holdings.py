"""
Kite Holdings Module
Provides functions to fetch and aggregate holdings from Kite API
Can be used as a library by multiple Python files
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from datetime import datetime
from typing import List, Optional

# Import models from parent directory
import sys
from pathlib import Path as PathLib
parent_dir = PathLib(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
from input_parsers.models import HoldingsData, StockHolding


def get_holdings_from_single_kite_account(api_key: str, access_token: str, account_name: str = None) -> List[StockHolding]:
    """
    Get holdings from a single Kite API account
    
    Args:
        api_key: Kite API key
        access_token: Kite access token
        account_name: Optional account identifier for logging
    
    Returns:
        List of StockHolding objects
    """
    # Initialize Kite Connect
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    
    # Get holdings from Kite
    account_label = f" ({account_name})" if account_name else ""
   # print(f"Fetching holdings from Kite API{account_label}...")
    
    try:
        kite_holdings = kite.holdings()
        
        # Convert to StockHolding objects
        holdings_list = []
        
        for h in kite_holdings:
            symbol = h.get('tradingsymbol', '')
            quantity = h.get('quantity', 0)
            last_price = h.get('last_price', 0)
            avg_price = h.get('average_price', 0)
            current_value = quantity * last_price if last_price else 0
            
            # Create StockHolding object
            stock_holding = StockHolding(
                symbol=symbol,
                quantity=quantity,
                price=last_price,  # Use last_price as current price
                value=current_value,
                company_name=h.get('tradingsymbol', ''),  # Kite doesn't provide company name directly
                sector=None,  # Kite doesn't provide sector
                exchange=h.get('exchange', ''),
                currency='INR',
                date=datetime.now()
            )
            holdings_list.append(stock_holding)
        
       # print(f"  Fetched {len(holdings_list)} holdings{account_label}")
        return holdings_list
        
    except Exception as e:
        print(f"  [ERROR] Failed to fetch holdings{account_label}: {e}")
        return []


def group_holdings_by_symbol(holdings: List[StockHolding]) -> List[StockHolding]:
    """
    Group and sum holdings by symbol (and exchange)
    
    Args:
        holdings: List of StockHolding objects to group
    
    Returns:
        List of grouped StockHolding objects
    """
    holdings_by_symbol = {}
    
    for holding in holdings:
        symbol = holding.symbol
        exchange = holding.exchange or ""
        # Use symbol+exchange as key to handle same symbol on different exchanges
        key = f"{exchange}:{symbol}" if exchange else symbol
        
        if key in holdings_by_symbol:
            # Aggregate: sum quantities and values
            existing = holdings_by_symbol[key]
            existing_qty_before = existing.quantity or 0
            new_qty = holding.quantity or 0
            existing.quantity = existing_qty_before + new_qty
            existing.value = (existing.value or 0) + (holding.value or 0)
            
            # Update price to weighted average if both have prices
            if existing.price and holding.price and abs(existing.quantity) >= 1:
                # Weighted average: (price1 * qty1 + price2 * qty2) / (qty1 + qty2)
                existing.price = ((existing.price * existing_qty_before) + 
                                 (holding.price * new_qty)) / existing.quantity
            elif holding.price and abs(existing.quantity) >= 1:
                # If existing doesn't have price, use new price
                existing.price = holding.price
            elif existing.quantity > 0 and existing.value:
                # Recalculate price from value if available
                existing.price = existing.value / existing.quantity
            
            # Keep the latest date
            if holding.date and (not existing.date or holding.date > existing.date):
                existing.date = holding.date
        else:
            # First occurrence of this symbol
            holdings_by_symbol[key] = StockHolding(
                symbol=holding.symbol,
                quantity=holding.quantity,
                price=holding.price,
                value=holding.value,
                company_name=holding.company_name,
                sector=holding.sector,
                exchange=holding.exchange,
                currency=holding.currency,
                date=holding.date
            )
    
    return list(holdings_by_symbol.values())


def get_holdings_from_kite(api_key: str = None, access_token: str = None, 
                           api_key_file: str = None, group_by_symbol: bool = True) -> HoldingsData:
    """
    Get holdings from Kite API and convert to HoldingsData format
    Supports single account or multiple accounts (semicolon-separated in env vars)
    
    Args:
        api_key: Optional single API key (if None, reads from env with support for multiple)
        access_token: Optional single access token (if None, reads from env with support for multiple)
        api_key_file: Optional path to API key file (defaults to api_key.env in parent directory)
        group_by_symbol: If True, group and sum holdings with same symbol (default: True)
    
    Returns:
        HoldingsData object with all holdings from all accounts
    """
    # Load API keys from file
    if api_key_file:
        api_key_path = Path(api_key_file)
    else:
        # Default to parent directory
        script_dir = Path(__file__).parent.parent
        api_key_path = script_dir / "api_key.env"
    
    if api_key_path.exists():
        load_dotenv(api_key_path)
    
    # If single key/token provided, use them
    if api_key and access_token:
        holdings_list = get_holdings_from_single_kite_account(api_key, access_token)
        
        # Group holdings by symbol if requested
        if group_by_symbol:
            holdings_list = group_holdings_by_symbol(holdings_list)
        
        total_value = sum(h.value or 0 for h in holdings_list)
        
        holdings_data = HoldingsData(
            holdings=holdings_list,
            source_file="Kite API",
            parse_date=datetime.now(),
            total_value=total_value
        )
        return holdings_data
    
    # Otherwise, check for multiple accounts in env vars
    KITE_API_KEYS = os.getenv('KITE_API_KEY', '')
    KITE_ACCESS_TOKENS = os.getenv('KITE_ACCESS_TOKEN', '')
    
    if not KITE_API_KEYS or not KITE_ACCESS_TOKENS:
        raise ValueError("KITE_API_KEY or KITE_ACCESS_TOKEN not found in api_key.env")
    
    # Split by semicolon to get multiple accounts
    api_keys = [k.strip() for k in KITE_API_KEYS.split(';') if k.strip()]
    access_tokens = [t.strip() for t in KITE_ACCESS_TOKENS.split(';') if t.strip()]
    
    if len(api_keys) != len(access_tokens):
        raise ValueError(f"Mismatch: {len(api_keys)} API keys but {len(access_tokens)} access tokens. "
                        f"Ensure they are semicolon-separated and match in count.")
    
    if len(api_keys) == 0:
        raise ValueError("No API keys found in KITE_API_KEY")
    
   # print(f"Found {len(api_keys)} Kite account(s)")
    #print("=" * 80)
    
    # Fetch holdings from all accounts
    all_holdings = []
    
    for i, (api_key, access_token) in enumerate(zip(api_keys, access_tokens), 1):
        account_name = f"Account {i}"
        holdings = get_holdings_from_single_kite_account(api_key, access_token, account_name)
        all_holdings.extend(holdings)
    
    #print("=" * 80)
    #print(f"Total holdings before grouping: {len(all_holdings)}")
    
    # Group holdings by symbol if requested
    if group_by_symbol:
        grouped_holdings = group_holdings_by_symbol(all_holdings)
     #   print(f"Total holdings after grouping: {len(grouped_holdings)}")
    else:
        grouped_holdings = all_holdings
    
    total_value = sum(h.value or 0 for h in grouped_holdings)
    #print(f"Total portfolio value: {total_value:,.2f}")
    
    # Create HoldingsData object with grouped holdings
    holdings_data = HoldingsData(
        holdings=grouped_holdings,
        source_file=f"Kite API ({len(api_keys)} accounts)",
        parse_date=datetime.now(),
        total_value=total_value
    )
    
    return holdings_data

