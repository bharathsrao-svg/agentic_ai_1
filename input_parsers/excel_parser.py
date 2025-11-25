"""
Excel parser for stock holdings files
Supports common formats: .xlsx, .xls
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import StockHolding, HoldingsData


class ExcelHoldingsParser:
    """Parser for extracting stock holdings from Excel files"""
    
    # Common column name variations (using sets for O(1) membership testing)
    SYMBOL_COLUMNS = {'symbol', 'ticker', 'stock', 'stock_symbol', 'ticker_symbol', 
                      'security', 'instrument', 'code'}
    QUANTITY_COLUMNS = {'quantity', 'qty', 'shares', 'units', 'number_of_shares', 'quantity available'}
    PRICE_COLUMNS = {'price', 'unit_price', 'cost_price', 'avg_price', 'purchase_price', 'previous closing price'}
    COST_PRICE_COLUMNS = {'cost_price', 'average price', 'purchase_price'}
    VALUE_COLUMNS = {'value', 'market_value', 'total_value', 'amount', 'current_value'}
    COMPANY_COLUMNS = {'company', 'company_name', 'name', 'security_name', 'description'}
    SECTOR_COLUMNS = {'sector', 'industry', 'industry_sector'}
    EXCHANGE_COLUMNS = {'exchange', 'market', 'listed_on'}
    
    def __init__(self):
        self.holdings = []
    
    def normalize_column_name(self, col: str) -> str:
        """Normalize column names for matching"""
        return re.sub(r'[_\s-]', '_', col.lower().strip())
    
    def find_column(self, df: pd.DataFrame, possible_names) -> Optional[str]:
        """Find column by matching against possible names
        
        Args:
            df: DataFrame to search
            possible_names: Set or list of possible column names
            
        Returns:
            First matching column name or None
        """
        normalized_cols = {self.normalize_column_name(col): col for col in df.columns}
        
        for name in possible_names:
            normalized_name = self.normalize_column_name(name)
            if normalized_name in normalized_cols:
                return normalized_cols[normalized_name]
        return None
    
    def parse_value(self, value) -> Optional[float]:
        """Parse numeric value, handling strings with commas, currency symbols, etc."""
        if pd.isna(value) or value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[₹$€£,\s]', '', value)
            # Extract number
            match = re.search(r'[\d.]+', cleaned)
            if match:
                return float(match.group())
        
        return None
    
    def parse_excel(self, file_path: str) -> HoldingsData:
        """
        Parse Excel file and extract stock holdings
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            HoldingsData object with parsed holdings
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try reading Excel file
        try:
            # Read all sheets - holdings might be in any sheet
            excel_file = pd.ExcelFile(file_path)
            df = None
            
            # Try to find the sheet with holdings data
            for sheet_name in excel_file.sheet_names:
                temp_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Check if this sheet has relevant columns
                if self._has_holdings_columns(temp_df):
                    df = temp_df
                    break
            
            # If no sheet found with holdings columns, use first sheet
            if df is None:
                df = pd.read_excel(excel_file, sheet_name=0)
            
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
        
        # Find relevant columns
        symbol_col = self.find_column(df, self.SYMBOL_COLUMNS)
        if not symbol_col:
            raise ValueError("Could not find symbol/ticker column in Excel file")
        
        quantity_col = self.find_column(df, self.QUANTITY_COLUMNS)
        price_col = self.find_column(df, self.PRICE_COLUMNS)
        value_col = self.find_column(df, self.VALUE_COLUMNS)
        company_col = self.find_column(df, self.COMPANY_COLUMNS)
        sector_col = self.find_column(df, self.SECTOR_COLUMNS)
        exchange_col = self.find_column(df, self.EXCHANGE_COLUMNS)
        
        # Parse holdings
        holdings = []
        for idx, row in df.iterrows():
            symbol = str(row[symbol_col]).strip() if pd.notna(row[symbol_col]) else None
            
            if not symbol or symbol.lower() in ['nan', 'none', '']:
                continue
            
            holding = StockHolding(
                symbol=symbol,
                company_name=str(row[company_col]).strip() if company_col and pd.notna(row[company_col]) else None,
                quantity=self.parse_value(row[quantity_col]) if quantity_col else None,
                price=self.parse_value(row[price_col]) if price_col else None,
                value=self.parse_value(row[value_col]) if value_col else None,
                sector=str(row[sector_col]).strip() if sector_col and pd.notna(row[sector_col]) else None,
                exchange=str(row[exchange_col]).strip() if exchange_col and pd.notna(row[exchange_col]) else None,
            )
            
            # Calculate value if not present but quantity and price are available
            if holding.value is None and holding.quantity and holding.price:
                holding.value = holding.quantity * holding.price
            
            holdings.append(holding)
        
        holdings_data = HoldingsData(
            holdings=holdings,
            source_file=str(file_path),
            parse_date=datetime.now()
        )
        holdings_data.calculate_total_value()
        
        return holdings_data
    
    def _has_holdings_columns(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has columns that suggest it contains holdings data"""
        normalized_cols = [self.normalize_column_name(col) for col in df.columns]
        
        # Check for symbol/ticker column
        symbol_found = any(
            self.normalize_column_name(name) in normalized_cols 
            for name in self.SYMBOL_COLUMNS
        )
        
        # Check for at least one of quantity, price, or value
        has_data_col = any(
            any(self.normalize_column_name(name) in normalized_cols for name in col_list)
            for col_list in [self.QUANTITY_COLUMNS, self.PRICE_COLUMNS, self.VALUE_COLUMNS]
        )
        
        return symbol_found and has_data_col

