"""
PDF parser for stock holdings files
Uses multiple strategies: table extraction, text parsing, and OCR if needed
"""
import re
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

from .models import StockHolding, HoldingsData


class PDFHoldingsParser:
    """Parser for extracting stock holdings from PDF files"""
    
    def __init__(self):
        self.holdings = []
        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            raise ImportError(
                "At least one PDF library is required. Install pdfplumber or PyPDF2: "
                "pip install pdfplumber or pip install PyPDF2"
            )
    
    def parse_value(self, text: str) -> Optional[float]:
        """Parse numeric value from text"""
        if not text or text.strip() == '':
            return None
        
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[₹$€£,\s]', '', str(text))
        # Extract number (including decimals)
        match = re.search(r'[\d.]+', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    def extract_symbol(self, text: str) -> Optional[str]:
        """Extract stock symbol from text"""
        if not text:
            return None
        
        text = str(text).strip().upper()
        # Common symbol patterns: 3-5 uppercase letters, sometimes with numbers
        symbol_pattern = r'\b([A-Z]{2,5}[A-Z0-9]*)\b'
        match = re.search(symbol_pattern, text)
        if match:
            symbol = match.group(1)
            # Filter out common non-symbol words
            if symbol not in ['THE', 'AND', 'LTD', 'INC', 'CORP', 'CO']:
                return symbol
        return None
    
    def parse_with_pdfplumber(self, file_path: Path) -> List[StockHolding]:
        """Parse PDF using pdfplumber (best for table extraction)"""
        holdings = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Try extracting tables first
                tables = page.extract_tables()
                
                if tables:
                    for table in tables:
                        holdings.extend(self._parse_table(table))
                
                # If no tables or table parsing failed, try text extraction
                if not tables:
                    text = page.extract_text()
                    if text:
                        holdings.extend(self._parse_text(text))
        
        return holdings
    
    def parse_with_pypdf2(self, file_path: Path) -> List[StockHolding]:
        """Parse PDF using PyPDF2 (fallback method)"""
        holdings = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    holdings.extend(self._parse_text(text))
        
        return holdings
    
    def _parse_table(self, table: List[List]) -> List[StockHolding]:
        """Parse holdings from a table structure"""
        holdings = []
        
        if not table or len(table) < 2:
            return holdings
        
        # Try to identify header row
        header_row_idx = 0
        headers = [str(cell).lower().strip() if cell else '' for cell in table[0]]
        
        # Find column indices
        symbol_idx = None
        quantity_idx = None
        price_idx = None
        value_idx = None
        company_idx = None
        sector_idx = None
        
        for idx, header in enumerate(headers):
            header_lower = header.lower()
            if any(x in header_lower for x in ['symbol', 'ticker', 'stock','scheme details']):
                symbol_idx = idx
            elif any(x in header_lower for x in ['quantity', 'qty', 'shares','units']):
                quantity_idx = idx
            elif any(x in header_lower for x in ['price', 'cost','nav']):
                price_idx = idx
            elif any(x in header_lower for x in ['value', 'amount', 'total']):
                value_idx = idx
            elif any(x in header_lower for x in ['company', 'name', 'security','scheme details']):
                company_idx = idx
            elif any(x in header_lower for x in ['sector', 'industry']):
                sector_idx = idx
        
        # Parse data rows
        for row in table[1:]:
            if not row or len(row) <= max(filter(None, [symbol_idx, quantity_idx, price_idx, value_idx])):
                continue
            
            symbol = None
            if symbol_idx is not None and symbol_idx < len(row):
                symbol = self.extract_symbol(str(row[symbol_idx])) if row[symbol_idx] else None
            
            if not symbol:
                # Try to extract symbol from any cell in the row
                for cell in row:
                    if cell:
                        symbol = self.extract_symbol(str(cell))
                        if symbol:
                            break
            
            if not symbol:
                continue
            
            holding = StockHolding(
                symbol=str(row[symbol_idx]).strip() if symbol_idx and symbol_idx < len(row) and row[symbol_idx] else None,
             #   symbol=symbol,
                company_name=str(row[company_idx]).strip() if company_idx and company_idx < len(row) and row[company_idx] else None,
                quantity=self.parse_value(str(row[quantity_idx])) if quantity_idx and quantity_idx < len(row) and row[quantity_idx] else None,
                price=self.parse_value(str(row[price_idx])) if price_idx and price_idx < len(row) and row[price_idx] else None,
                value=self.parse_value(str(row[value_idx])) if value_idx and value_idx < len(row) and row[value_idx] else None,
                sector=str(row[sector_idx]).strip() if sector_idx and sector_idx < len(row) and row[sector_idx] else None,
            )
            
            # Calculate value if not present
            if holding.value is None and holding.quantity and holding.price:
                holding.value = holding.quantity * holding.price
            
            holdings.append(holding)
        
        return holdings
    
    def _parse_text(self, text: str) -> List[StockHolding]:
        """Parse holdings from unstructured text"""
        holdings = []
        lines = text.split('\n')
        
        # Pattern to match lines with symbol, quantity, price, value
        # Example: "AAPL    100    150.50    15050.00"
        pattern = r'([A-Z]{2,5}[A-Z0-9]*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try pattern matching
            match = re.search(pattern, line)
            if match:
                symbol = match.group(1)
                quantity = self.parse_value(match.group(2))
                price = self.parse_value(match.group(3))
                value = self.parse_value(match.group(4))
                
                holding = StockHolding(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    value=value or (quantity * price if quantity and price else None)
                )
                holdings.append(holding)
            else:
                # Try to extract just symbol if found
                symbol = self.extract_symbol(line)
                if symbol and len(symbol) >= 2:
                    # Look for numbers in the same line
                    numbers = re.findall(r'[\d,]+\.?\d*', line)
                    if len(numbers) >= 2:
                        holding = StockHolding(
                            symbol=symbol,
                            quantity=self.parse_value(numbers[0]),
                            price=self.parse_value(numbers[1]) if len(numbers) > 1 else None,
                            value=self.parse_value(numbers[2]) if len(numbers) > 2 else None
                        )
                        if holding.quantity or holding.price or holding.value:
                            holdings.append(holding)
        
        return holdings
    
    def parse_pdf(self, file_path: str) -> HoldingsData:
        """
        Parse PDF file and extract stock holdings
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            HoldingsData object with parsed holdings
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        holdings = []
        
        # Try pdfplumber first (better for tables)
        if PDFPLUMBER_AVAILABLE:
            try:
                holdings = self.parse_with_pdfplumber(file_path)
            except Exception as e:
                print(f"Error with pdfplumber: {e}")
                holdings = []
        
        # Fallback to PyPDF2 if pdfplumber failed or not available
        if not holdings and PYPDF2_AVAILABLE:
            try:
                holdings = self.parse_with_pypdf2(file_path)
            except Exception as e:
                print(f"Error with PyPDF2: {e}")
                holdings = []
        
        if not holdings:
            raise ValueError("Could not extract holdings from PDF. The file might be image-based or have an unsupported format.")
        
        # Remove duplicates based on symbol
        seen_symbols = set()
        unique_holdings = []
        for holding in holdings:
            if holding.symbol and holding.symbol not in seen_symbols:
                seen_symbols.add(holding.symbol)
                unique_holdings.append(holding)
        
        holdings_data = HoldingsData(
            holdings=unique_holdings,
            source_file=str(file_path),
            parse_date=datetime.now()
        )
        holdings_data.calculate_total_value()
        
        return holdings_data

