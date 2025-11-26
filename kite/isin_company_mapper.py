"""
ISIN to Company Name Mapper Module
Loads company name mapping from CSV file and enriches StockHolding objects with company names
"""
import csv
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import sys

# Import models from parent directory
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
from input_parsers.models import StockHolding


# Cache for ISIN to company name mapping
_isin_to_company_cache: Optional[Dict[str, str]] = None
_symbol_to_company_cache: Optional[Dict[str, str]] = None


def load_company_mapping(csv_file_path: Optional[Path] = None) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Load ISIN to company name mapping from CSV file
    
    Args:
        csv_file_path: Path to company_names.csv file. If None, uses default location
    
    Returns:
        Tuple of (isin_to_company_dict, symbol_to_company_dict)
    """
    global _isin_to_company_cache, _symbol_to_company_cache
    
    # Return cached data if already loaded
    if _isin_to_company_cache is not None and _symbol_to_company_cache is not None:
        return _isin_to_company_cache, _symbol_to_company_cache
    
    # Default CSV file path
    if csv_file_path is None:
        script_dir = Path(__file__).parent.parent
        csv_file_path = script_dir / "data" / "company_names.csv"
    
    if not csv_file_path.exists():
        raise FileNotFoundError(f"Company names CSV file not found: {csv_file_path}")
    
    isin_to_company = {}
    symbol_to_company = {}
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Clean column names (remove extra spaces)
            isin = row.get('ISIN NUMBER', '').strip()
            company_name = row.get('NAME OF COMPANY', '').strip()
            symbol = row.get('SYMBOL', '').strip()
            
            if isin and company_name:
                isin_to_company[isin] = company_name
            
            if symbol and company_name:
                symbol_to_company[symbol] = company_name
    
    # Cache the results
    _isin_to_company_cache = isin_to_company
    _symbol_to_company_cache = symbol_to_company
    
    return isin_to_company, symbol_to_company


def get_company_name_from_isin(isin: str, csv_file_path: Optional[Path] = None) -> Optional[str]:
    """
    Get company name from ISIN
    
    Args:
        isin: ISIN code
        csv_file_path: Optional path to CSV file
    
    Returns:
        Company name if found, None otherwise
    """
    isin_to_company, _ = load_company_mapping(csv_file_path)
    return isin_to_company.get(isin.strip() if isin else '')


def get_company_name_from_symbol(symbol: str, csv_file_path: Optional[Path] = None) -> Optional[str]:
    """
    Get company name from symbol (fallback method)
    
    Args:
        symbol: Trading symbol
        csv_file_path: Optional path to CSV file
    
    Returns:
        Company name if found, None otherwise
    """
    _, symbol_to_company = load_company_mapping(csv_file_path)
    return symbol_to_company.get(symbol.strip() if symbol else '')


def enrich_holding_with_company_name(holding: StockHolding, 
                                     kite_holding_data: Optional[dict] = None,
                                     csv_file_path: Optional[Path] = None) -> StockHolding:
    """
    Enrich a StockHolding object with company name from ISIN
    
    Args:
        holding: StockHolding object to enrich
        kite_holding_data: Optional raw kite holding data dict (to extract ISIN)
        csv_file_path: Optional path to CSV file
    
    Returns:
        StockHolding object with updated company_name (if found)
    """
    # Try to get ISIN from kite_holding_data if provided
    isin = None
    if kite_holding_data:
        # Kite API might return ISIN in different field names
        isin = (kite_holding_data.get('isin') or 
                kite_holding_data.get('isin_code') or 
                kite_holding_data.get('ISIN') or
                kite_holding_data.get('ISIN_CODE'))
    
    # Try to get company name from ISIN
    if isin:
        company_name = get_company_name_from_isin(isin, csv_file_path)
        if company_name:
            holding.company_name = company_name
            return holding
    
    # Fallback: Try to get company name from symbol
    if holding.symbol:
        company_name = get_company_name_from_symbol(holding.symbol, csv_file_path)
        if company_name:
            holding.company_name = company_name
    
    return holding


def enrich_holdings_with_company_names(holdings: List[StockHolding],
                                      kite_holdings_data: Optional[List[dict]] = None,
                                      csv_file_path: Optional[Path] = None) -> List[StockHolding]:
    """
    Enrich a list of StockHolding objects with company names from ISIN
    
    Args:
        holdings: List of StockHolding objects to enrich
        kite_holdings_data: Optional list of raw kite holding data dicts (to extract ISIN)
        csv_file_path: Optional path to CSV file
    
    Returns:
        List of StockHolding objects with updated company_name (where found)
    """
    # Create a mapping from symbol to kite holding data for quick lookup
    kite_data_map = {}
    if kite_holdings_data:
        for kite_data in kite_holdings_data:
            symbol = kite_data.get('tradingsymbol', '')
            if symbol:
                kite_data_map[symbol] = kite_data
    
    # Enrich each holding
    enriched_holdings = []
    for holding in holdings:
        kite_data = kite_data_map.get(holding.symbol) if holding.symbol else None
        enriched_holding = enrich_holding_with_company_name(holding, kite_data, csv_file_path)
        enriched_holdings.append(enriched_holding)
    
    return enriched_holdings

