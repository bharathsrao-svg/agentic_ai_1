"""
Example: Integrating holdings parser with your Agentic AI app
"""
from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from input_parsers.parser_factory import HoldingsParserFactory
import json


def analyze_portfolio_with_ai(holdings_file_path: str):
    """
    Parse holdings and get AI analysis
    """
    # Step 1: Parse the holdings file
    print(f"Parsing holdings from: {holdings_file_path}")
    holdings_data = HoldingsParserFactory.parse_file(holdings_file_path)
    
    # Step 2: Prepare summary for AI
    portfolio_summary = {
        "total_holdings": len(holdings_data.holdings),
        "total_value": holdings_data.total_value,
        "holdings": [
            {
                "symbol": h.symbol,
                "company": h.company_name,
                "quantity": h.quantity,
                "price": h.price,
                "value": h.value,
                "sector": h.sector
            }
            for h in holdings_data.holdings
        ]
    }
    
    # Step 3: Create prompt with holdings data
    holdings_json = json.dumps(portfolio_summary, indent=2, default=str)
    
    template = """You are a financial advisor AI assistant. Analyze the following stock portfolio holdings and provide insights:

Portfolio Data:
{holdings_data}

Please provide:
1. Portfolio overview (total value, number of holdings)
2. Sector diversification analysis
3. Top holdings by value
4. Any recommendations or observations

Answer in a clear, structured format."""

    prompt = PromptTemplate(
        input_variables=["holdings_data"],
        template=template
    )
    
    # Step 4: Get AI analysis
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    print("\n" + "="*80)
    print("Getting AI Analysis...")
    print("="*80 + "\n")
    
    response = chain.run(holdings_data=holdings_json)
    return response, holdings_data


def ask_question_about_holdings(holdings_file_path: str, question: str):
    """
    Parse holdings and ask a specific question to the AI
    """
    # Parse holdings
    holdings_data = HoldingsParserFactory.parse_file(holdings_file_path)
    
    # Convert to JSON for context
    holdings_json = json.dumps(holdings_data.to_dict(), indent=2, default=str)
    
    # Create prompt
    template = """You are analyzing a stock portfolio. Here is the portfolio data:

{holdings_data}

Question: {question}

Provide a detailed answer based on the portfolio data above."""

    prompt = PromptTemplate(
        input_variables=["holdings_data", "question"],
        template=template
    )
    
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    response = chain.run(holdings_data=holdings_json, question=question)
    return response


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent_with_holdings.py <holdings_file_path> [question]")
        print("\nExamples:")
        print("  python agent_with_holdings.py holdings.pdf")
        print("  python agent_with_holdings.py holdings.pdf 'What is my sector diversification?'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else None
    
    if question:
        # Ask specific question
        print(f"Question: {question}\n")
        answer = ask_question_about_holdings(file_path, question)
        print(answer)
    else:
        # Full portfolio analysis
        analysis, holdings_data = analyze_portfolio_with_ai(file_path)
        print(analysis)

