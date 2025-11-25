"""
Analyze holdings from database using LangChain LLM
Extracts holdings data, formats for LLM, and provides comprehensive analysis
"""
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List, Dict

from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate

from input_parsers.db_persistence import HoldingsDBPersistence


class HoldingsAnalyzer:
    """Analyze holdings from database using LLM"""
    
    def __init__(self, llm_model: str = "sonar", temperature: float = 0.7, 
                 api_key_file: Optional[str] = None):
        """
        Initialize the analyzer
        
        Args:
            llm_model: LLM model name (default: "sonar")
            temperature: Temperature for LLM (default: 0.7)
            api_key_file: Path to API key file (default: "api_key.env")
        """
        # Load API key from file if provided
        if api_key_file:
            api_key_path = Path(api_key_file)
            if api_key_path.exists():
                load_dotenv(api_key_path)
                print(f"Loaded API key from: {api_key_path}")
            else:
                print(f"Warning: API key file not found: {api_key_path}")
        
        self.llm = ChatPerplexity(model=llm_model, temperature=temperature)
        self.analysis_prompt = self._create_analysis_prompt()
        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
    
    def _create_analysis_prompt(self) -> PromptTemplate:
        """Create the prompt template for holdings analysis"""
        template = """You are an expert financial advisor and portfolio analyst. Analyze the following stock holdings portfolio and provide a comprehensive consolidated analysis.

PORTFOLIO HOLDINGS DATA:
{
}

Please provide a detailed consolidated analysis report including:

1. **Portfolio Overview:**
   - Total portfolio value
   - Number of holdings
   - Average holding size
   - Portfolio composition summary

2. **Individual Holdings Analysis:**
   For each holding, provide:
   - Symbol and Company Name
   - Current Holding Value
   - Estimated 1-year returns (based on current market conditions and historical performance)
   - Recommendation: BUY / SELL / RETAIN with reasoning
   - Risk assessment
   - Sector/Industry context

3. **Sector Diversification:**
   - Sector-wise allocation
   - Diversification quality
   - Concentration risks

4. **Overall Recommendations:**
   - Top 3 holdings to consider selling (if any)
   - Top 3 holdings to consider buying more (if any)
   - Holdings to retain as-is
   - Portfolio rebalancing suggestions

5. **Risk Assessment:**
   - Overall portfolio risk level
   - Key risk factors
   - Mitigation strategies

Please format your response in a clear, structured manner with sections and bullet points. Be specific with your recommendations and provide actionable insights.

ANALYSIS:"""
        
        return PromptTemplate(
            input_variables=["holdings_data"],
            template=template
        )
    
    def format_holdings_for_llm(self, holdings: List[Dict]) -> str:
        """
        Format holdings data for LLM consumption
        
        Args:
            holdings: List of holding dictionaries from database
            
        Returns:
            Formatted string for LLM
        """
        if not holdings:
            return "No holdings found in the portfolio."
        
        # Calculate totals
        total_value = sum(h.get('value', 0) or 0 for h in holdings)
        total_holdings = len(holdings)
        
        # Group by sector
        sector_breakdown = {}
        for h in holdings:
            sector = h.get('sector') or 'Uncategorized'
            if sector not in sector_breakdown:
                sector_breakdown[sector] = {'count': 0, 'value': 0, 'holdings': []}
            sector_breakdown[sector]['count'] += 1
            sector_breakdown[sector]['value'] += h.get('value', 0) or 0
            sector_breakdown[sector]['holdings'].append(h)
        
        # Format output
        formatted = f"""
=== PORTFOLIO SUMMARY ===
Total Holdings: {total_holdings}
Total Portfolio Value: {total_value:,.2f}
Average Holding Value: {total_value/total_holdings:,.2f}

=== SECTOR BREAKDOWN ===
"""
        for sector, data in sorted(sector_breakdown.items(), 
                                   key=lambda x: x[1]['value'], reverse=True):
            pct = (data['value'] / total_value * 100) if total_value > 0 else 0
            formatted += f"\n{sector}: {data['count']} holdings, {data['value']:,.2f} ({pct:.1f}%)\n"
        
        formatted += "\n=== INDIVIDUAL HOLDINGS ===\n\n"
        
        # Sort by value descending
        sorted_holdings = sorted(holdings, key=lambda h: h.get('value', 0) or 0, reverse=True)
        
        for i, holding in enumerate(sorted_holdings, 1):
            formatted += f"""
{i}. {holding.get('symbol', 'N/A')} - {holding.get('company_name', 'N/A') or 'N/A'}
   - Quantity: {holding.get('quantity', 'N/A')}
   - Price: {holding.get('price', 'N/A')}
   - Current Value: {holding.get('value', 0) or 0:,.2f}
   - Sector: {holding.get('sector', 'N/A') or 'N/A'}
   - Exchange: {holding.get('exchange', 'N/A') or 'N/A'}
"""
        
        return formatted
    
    def analyze_holdings(self, holdings: List[Dict], custom_query: Optional[str] = None) -> str:
        """
        Analyze holdings using LLM
        
        Args:
            holdings: List of holding dictionaries
            custom_query: Optional custom query to override default analysis
            
        Returns:
            LLM analysis response
        """
        # Format holdings for LLM
        formatted_holdings = self.format_holdings_for_llm(holdings)
        
        # Use custom query if provided, otherwise use default
        if custom_query:
            custom_prompt = PromptTemplate(
                input_variables=["holdings_data"],
                template=f"""You are an expert financial advisor. Analyze the following portfolio holdings:

{{holdings_data}}

{custom_query}

Provide a detailed, structured response."""
            )
            custom_chain = LLMChain(llm=self.llm, prompt=custom_prompt)
            response = custom_chain.run(holdings_data=formatted_holdings)
        else:
            response = self.chain.run(holdings_data=formatted_holdings)
        
        return response
    
    def analyze_from_db(self, import_id: Optional[int] = None, 
                       source_file: Optional[str] = None,
                       custom_query: Optional[str] = None) -> str:
        """
        Extract holdings from database and analyze
        
        Args:
            import_id: Specific import ID to analyze (optional)
            source_file: Source file name to analyze (optional, uses latest if not specified)
            custom_query: Custom analysis query (optional)
            
        Returns:
            LLM analysis response
        """
        with HoldingsDBPersistence() as db:
            if import_id:
                # Get holdings for specific import
                holdings = db.get_holdings_by_import_id(import_id)
                if not holdings:
                    return f"No holdings found for import_id: {import_id}"
            elif source_file:
                # Get latest import for this file
                imports = db.get_latest_imports(limit=100)
                matching_imports = [imp for imp in imports if imp['source_file'] == source_file]
                if not matching_imports:
                    return f"No imports found for file: {source_file}"
                import_id = matching_imports[0]['id']
                holdings = db.get_holdings_by_import_id(import_id)
            else:
                # Get latest import
                imports = db.get_latest_imports(limit=1)
                if not imports:
                    return "No holdings found in database. Please import holdings first."
                import_id = imports[0]['id']
                holdings = db.get_holdings_by_import_id(import_id)
                print(f"Analyzing latest import (ID: {import_id})")
            
            if not holdings:
                return "No holdings found to analyze."
            
            print(f"Analyzing {len(holdings)} holdings...")
            return self.analyze_holdings(holdings, custom_query)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze holdings from database using LLM'
    )
    parser.add_argument('--import-id', type=int, 
                       help='Analyze specific import ID')
    parser.add_argument('--source-file', type=str,
                       help='Analyze holdings from specific source file')
    parser.add_argument('--config', help='Path to database config file (.env)', 
                       default='input_parsers/db_config.env')
    parser.add_argument('--query', type=str,
                       help='Custom analysis query (optional)')
    parser.add_argument('--model', type=str, default='sonar',
                       help='LLM model to use (default: sonar)')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='LLM temperature (default: 0.7)')
    parser.add_argument('--api-key-file', type=str, default='api_key.env',
                       help='Path to API key file (default: api_key.env)')
    parser.add_argument('--output', type=str,
                       help='Save analysis to file (optional)')
    
    args = parser.parse_args()
    
    # Load database config
    config_path = Path(args.config)
    if config_path.exists():
        load_dotenv(config_path)
    
    # Load API key from file
    api_key_path = Path(args.api_key_file)
    if api_key_path.exists():
        load_dotenv(api_key_path)
        print(f"Loaded API key from: {api_key_path}")
    else:
        print(f"Warning: API key file not found: {api_key_path}")
        print("Make sure PPLX_API_KEY is set in environment or api_key.env file")
    
    # Default query
    default_query = """Analyze this holdings file and share with me a consolidated file of analysis including:
1. 1 year returns for each holding
2. My holding value
3. Recommendation of whether I should buy or sell or retain this holding"""
    
    custom_query = args.query or default_query
    
    try:

        analyzer = HoldingsAnalyzer(
            llm_model=args.model,
            temperature=args.temperature,
            api_key_file=args.api_key_file
        )
        
        print("=" * 80)
        print("HOLDINGS ANALYSIS")
        print("=" * 80)
        print()
        
        analysis = analyzer.analyze_from_db(
            import_id=args.import_id,
            source_file=args.source_file,
            custom_query=custom_query
        )
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print()
        print(analysis)
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(analysis)
            print(f"\nAnalysis saved to: {output_path}")
        
        return analysis
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

