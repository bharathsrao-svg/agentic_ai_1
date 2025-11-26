# LLM Analysis Improvements - Quick Reference

## Created Files

1. **`llm_analysis_helper.py`** - Core helper functions with:
   - JSON extraction and validation
   - Retry logic with self-correction
   - Improved prompts with examples
   - Per-symbol analysis
   - Response validation

2. **`llm_integration_example.py`** - 5 different strategies you can use

3. **`llm_analysis_improvements.md`** - Detailed list of all improvement ideas

## Quick Start: Replace Your Current LLM Code

### Current Code (in agent_with_holdings.py):
```python
llm = ChatPerplexity(model="sonar", temperature=0.7)
chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run(holdings_data=holdings_json)
print(response)
```

### Improved Code (Option 1 - Simple):
```python
from kite.llm_analysis_helper import analyze_with_retry

llm = ChatPerplexity(model="sonar", temperature=0.5)
analysis_result = analyze_with_retry(
    llm=llm,
    holdings_data=holdings_json,
    max_retries=3,
    temperature=0.5
)

if "error" not in analysis_result:
    print(json.dumps(analysis_result, indent=2, default=str))
else:
    print(f"Error: {analysis_result['error']}")
```

### Improved Code (Option 2 - Per Symbol):
```python
from kite.llm_analysis_helper import analyze_holdings_per_symbol, combine_analyses

llm = ChatPerplexity(model="sonar", temperature=0.5)
per_symbol_results = analyze_holdings_per_symbol(
    llm=llm,
    holdings=portfolio_summary["holdings"],
    temperature=0.5
)
analysis_result = combine_analyses(per_symbol_results)
print(json.dumps(analysis_result, indent=2, default=str))
```

## Key Improvements

### 1. **Automatic Retry with Validation**
- Validates JSON structure
- Retries up to 3 times if validation fails
- Self-correction prompts for fixing errors

### 2. **Better Prompts**
- Role-playing ("senior equity research analyst")
- Clear examples of good responses
- Specific instructions about dates and sources
- Confidence score guidelines

### 3. **Temperature Tuning**
- Lower temperature (0.3-0.5) for focused, factual responses
- Higher temperature (0.7-0.9) for creative analysis
- Adaptive: start low, increase if confidence is low

### 4. **Per-Symbol Analysis**
- Analyze each holding separately for better focus
- Combine results into unified response
- Better for detailed analysis of individual stocks

### 5. **JSON Extraction**
- Handles markdown code blocks
- Extracts JSON from various response formats
- Robust parsing with fallbacks

## Recommended Strategy

**For most use cases, use Strategy 1 (Single Call with Retry):**
- Fast and efficient
- Good balance of quality and speed
- Automatic error handling
- Validated output

**For detailed analysis, use Strategy 2 (Per-Symbol):**
- More focused analysis per stock
- Better for portfolios with diverse holdings
- Slightly slower but more thorough

## Testing Different Approaches

Try these variations to see what works best:

1. **Model comparison**: Try "sonar", "sonar-pro", "llama-3.1-sonar-large-128k-online"
2. **Temperature**: Test 0.3, 0.5, 0.7, 0.9
3. **Retry count**: 2-3 retries usually sufficient
4. **Prompt style**: Compare role-playing vs. direct instructions

## Next Steps

1. Import the helper module in `agent_with_holdings.py`
2. Replace the current LLM code with one of the strategies
3. Test with your actual holdings data
4. Adjust temperature and model based on results
5. Consider adding more context (market indices, sector data) to prompts

