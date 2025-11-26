"""
Example: How to integrate improved LLM analysis into agent_with_holdings.py

This shows different strategies you can use to improve LLM results
"""

from langchain_community.chat_models import ChatPerplexity
from kite.llm_analysis_helper import (
    analyze_with_retry,
    analyze_holdings_per_symbol,
    combine_analyses,
    extract_json_from_response,
    validate_analysis_response
)
import json


# ============================================================================
# STRATEGY 1: Improved Single Call with Retry and Validation
# ============================================================================
def analyze_holdings_strategy1(holdings_json: str):
    """
    Single improved call with retry logic and validation
    Best for: Quick analysis, fewer tokens, faster results
    """
    llm = ChatPerplexity(model="sonar", temperature=0.5)  # Lower temp for more focused
    
    result = analyze_with_retry(
        llm=llm,
        holdings_data=holdings_json,
        max_retries=3,
        temperature=0.5
    )
    
    if "error" in result:
        print(f"Analysis failed: {result['error']}")
        return None
    
    return result


# ============================================================================
# STRATEGY 2: Per-Symbol Analysis (More Focused)
# ============================================================================
def analyze_holdings_strategy2(holdings_list: list):
    """
    Analyze each holding separately, then combine
    Best for: More detailed analysis, better focus per stock
    """
    llm = ChatPerplexity(model="sonar", temperature=0.5)
    
    # Analyze each holding separately
    per_symbol_results = analyze_holdings_per_symbol(
        llm=llm,
        holdings=holdings_list,
        temperature=0.5
    )
    
    # Combine results
    combined = combine_analyses(per_symbol_results)
    
    return combined


# ============================================================================
# STRATEGY 3: Two-Pass Analysis (Summary + Deep Dive)
# ============================================================================
def analyze_holdings_strategy3(holdings_json: str, holdings_list: list):
    """
    First pass: Quick summary
    Second pass: Deep dive into top movements
    Best for: Comprehensive analysis with focus on important movements
    """
    llm = ChatPerplexity(model="sonar", temperature=0.5)
    
    # Pass 1: Quick summary
    print("[Pass 1] Getting quick summary...")
    summary_result = analyze_with_retry(
        llm=llm,
        holdings_data=holdings_json,
        max_retries=2,
        temperature=0.3  # Very focused for summary
    )
    
    # Identify top movements (highest variation or value)
    top_holdings = sorted(
        holdings_list,
        key=lambda h: abs(h.get('variation_percent', 0)) * h.get('value', 0),
        reverse=True
    )[:5]  # Top 5
    
    # Pass 2: Deep dive on top holdings
    if top_holdings:
        print(f"[Pass 2] Deep dive on top {len(top_holdings)} holdings...")
        top_holdings_json = json.dumps({
            "holdings": top_holdings,
            "note": "These are the top holdings by price movement significance"
        }, indent=2, default=str)
        
        deep_dive_result = analyze_with_retry(
            llm=llm,
            holdings_data=top_holdings_json,
            max_retries=2,
            temperature=0.7  # More creative for deep analysis
        )
        
        # Combine results
        return {
            "summary": summary_result,
            "deep_dive": deep_dive_result,
            "top_holdings_analyzed": [h.get('symbol') for h in top_holdings]
        }
    
    return {"summary": summary_result}


# ============================================================================
# STRATEGY 4: Adaptive Temperature Based on Confidence
# ============================================================================
def analyze_holdings_strategy4(holdings_json: str):
    """
    Start with low temperature, if confidence is low, retry with higher temperature
    Best for: Balancing accuracy and creativity
    """
    llm = ChatPerplexity(model="sonar")
    
    # First attempt: Low temperature (focused)
    result = analyze_with_retry(
        llm=llm,
        holdings_data=holdings_json,
        max_retries=2,
        temperature=0.3
    )
    
    # Check overall confidence
    if result and "overall_confidence" in result:
        confidence = result["overall_confidence"]
        
        if confidence < 0.5:
            print(f"Low confidence ({confidence:.2f}), retrying with higher temperature...")
            # Retry with higher temperature for more creative analysis
            result = analyze_with_retry(
                llm=llm,
                holdings_data=holdings_json,
                max_retries=2,
                temperature=0.8
            )
    
    return result


# ============================================================================
# STRATEGY 5: Model Comparison (Try Multiple Models)
# ============================================================================
def analyze_holdings_strategy5(holdings_json: str):
    """
    Try multiple models and pick the best result
    Best for: Finding the best model for your use case
    """
    models = ["sonar", "sonar-pro", "llama-3.1-sonar-large-128k-online"]
    results = []
    
    for model_name in models:
        print(f"Trying model: {model_name}")
        try:
            llm = ChatPerplexity(model=model_name, temperature=0.5)
            result = analyze_with_retry(
                llm=llm,
                holdings_data=holdings_json,
                max_retries=2,
                temperature=0.5
            )
            
            if result and "overall_confidence" in result:
                results.append({
                    "model": model_name,
                    "result": result,
                    "confidence": result["overall_confidence"]
                })
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
    
    # Return result with highest confidence
    if results:
        best = max(results, key=lambda x: x["confidence"])
        return best["result"]
    
    return None


# ============================================================================
# INTEGRATION EXAMPLE: How to use in agent_with_holdings.py
# ============================================================================
"""
# In agent_with_holdings.py, replace the LLM analysis section with:

from kite.llm_analysis_helper import analyze_with_retry, analyze_holdings_per_symbol, combine_analyses

# ... existing code ...

# Step 4: Get AI analysis on filtered holdings (only if run_llm is True)
run_llm = getattr(args, 'run_llm', False)
if run_llm:
    print(f"\n[Step 4] Getting AI Analysis on filtered holdings...")
    print("=" * 80)
    
    # Prepare summary for AI
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
    
    holdings_json = json.dumps(portfolio_summary, indent=2, default=str)
    
    # Choose your strategy:
    # Option 1: Single improved call with retry
    llm = ChatPerplexity(model="sonar", temperature=0.5)
    analysis_result = analyze_with_retry(
        llm=llm,
        holdings_data=holdings_json,
        max_retries=3,
        temperature=0.5
    )
    
    # Option 2: Per-symbol analysis (uncomment to use)
    # analysis_result = analyze_holdings_strategy2(portfolio_summary["holdings"])
    
    # Display results
    if "error" not in analysis_result:
        print("\n" + "="*80)
        print("AI Analysis Results:")
        print("="*80)
        print(json.dumps(analysis_result, indent=2, default=str))
    else:
        print(f"\n[ERROR] Analysis failed: {analysis_result.get('error')}")
"""

