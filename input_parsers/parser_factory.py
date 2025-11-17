"""
Factory for creating appropriate parser based on file type
"""
from pathlib import Path
from typing import Union

from .excel_parser import ExcelHoldingsParser
from .pdf_parser import PDFHoldingsParser
from .models import HoldingsData


class HoldingsParserFactory:
    """Factory class to create appropriate parser based on file extension"""
    
    SUPPORTED_EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.xlsm'}
    SUPPORTED_PDF_EXTENSIONS = {'.pdf'}
    
    @staticmethod
    def get_parser(file_path: Union[str, Path]) -> Union[ExcelHoldingsParser, PDFHoldingsParser]:
        """
        Get appropriate parser for the file type
        
        Args:
            file_path: Path to the holdings file
            
        Returns:
            Appropriate parser instance
            
        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension in HoldingsParserFactory.SUPPORTED_EXCEL_EXTENSIONS:
            return ExcelHoldingsParser()
        elif extension in HoldingsParserFactory.SUPPORTED_PDF_EXTENSIONS:
            return PDFHoldingsParser()
        else:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {HoldingsParserFactory.SUPPORTED_EXCEL_EXTENSIONS | HoldingsParserFactory.SUPPORTED_PDF_EXTENSIONS}"
            )
    
    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> HoldingsData:
        """
        Parse a holdings file using the appropriate parser
        
        Args:
            file_path: Path to the holdings file
            
        Returns:
            HoldingsData object with parsed holdings
        """
        parser = HoldingsParserFactory.get_parser(file_path)
        
        if isinstance(parser, ExcelHoldingsParser):
            return parser.parse_excel(file_path)
        elif isinstance(parser, PDFHoldingsParser):
            return parser.parse_pdf(file_path)
        else:
            raise ValueError("Unknown parser type")

