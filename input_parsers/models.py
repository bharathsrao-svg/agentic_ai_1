"""
Data models for stock holdings
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class StockHolding:
    """Represents a single stock holding entry"""
    symbol: str
    company_name: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    value: Optional[float] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    date: Optional[datetime] = None
    yesterday_price: Optional[float] = None  # Previous day's price (for comparison)
    variation_percent: Optional[float] = None  # Percentage change from previous day
    
    def to_dict(self) -> dict:
        """Convert holding to dictionary"""
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'quantity': self.quantity,
            'price': self.price,
            'value': self.value,
            'sector': self.sector,
            'exchange': self.exchange,
            'currency': self.currency,
            'date': self.date.isoformat() if self.date else None,
            'yesterday_price': self.yesterday_price,
            'variation_percent': self.variation_percent
        }


@dataclass
class HoldingsData:
    """Container for parsed holdings data"""
    holdings: List[StockHolding]
    source_file: str
    parse_date: datetime
    total_value: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert holdings data to dictionary"""
        return {
            'source_file': self.source_file,
            'parse_date': self.parse_date.isoformat(),
            'total_value': self.total_value,
            'holdings': [h.to_dict() for h in self.holdings],
            'count': len(self.holdings)
        }
    
    def calculate_total_value(self):
        """Calculate total value from holdings"""
        self.total_value = sum(h.value or 0 for h in self.holdings if h.value)

