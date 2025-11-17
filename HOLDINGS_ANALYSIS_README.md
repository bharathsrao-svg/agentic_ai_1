# Holdings Analysis with LangChain LLM

This module extracts holdings from the PostgreSQL database, formats them for LLM consumption, and provides comprehensive AI-powered analysis.

## Features

- ✅ Extract holdings from database
- ✅ Format holdings data as tokens for LLM
- ✅ Comprehensive portfolio analysis with LangChain
- ✅ Recommendations: BUY/SELL/RETAIN for each holding
- ✅ 1-year return estimates
- ✅ Sector diversification analysis
- ✅ Risk assessment

## Usage

### 1. Simple Analysis (Latest Holdings)

```bash
python analyze_holdings_simple.py
```

This will:
- Extract the latest holdings from database
- Analyze with the default query
- Save results to `holdings_analysis.txt`

### 2. Advanced Analysis

```bash
# Analyze latest holdings
python analyze_holdings_from_db.py

# Analyze specific import ID
python analyze_holdings_from_db.py --import-id 1

# Analyze specific source file
python analyze_holdings_from_db.py --source-file "holdings_files/mf_holdings_1.pdf"

# Custom query
python analyze_holdings_from_db.py --query "Focus on risk analysis and sector concentration"

# Save to file
python analyze_holdings_from_db.py --output analysis_report.txt

# Use different LLM model
python analyze_holdings_from_db.py --model "sonar" --temperature 0.7
```

### 3. Programmatic Usage

```python
from analyze_holdings_from_db import HoldingsAnalyzer
from input_parsers.db_persistence import HoldingsDBPersistence

# Initialize analyzer
analyzer = HoldingsAnalyzer()

# Analyze latest holdings
analysis = analyzer.analyze_from_db()

# Analyze specific import
analysis = analyzer.analyze_from_db(import_id=1)

# Custom query
custom_query = """Analyze this holdings file and share with me a consolidated file of analysis including:
1. 1 year returns for each holding
2. My holding value
3. Recommendation of whether I should buy or sell or retain this holding"""

analysis = analyzer.analyze_from_db(custom_query=custom_query)
print(analysis)
```

## Default Analysis Query

The default query includes:
- 1-year returns for each holding
- Current holding values
- BUY/SELL/RETAIN recommendations
- Sector diversification
- Risk assessment
- Portfolio rebalancing suggestions

## Output Format

The analysis includes:

1. **Portfolio Overview**
   - Total portfolio value
   - Number of holdings
   - Average holding size

2. **Individual Holdings Analysis**
   - Symbol and company name
   - Current holding value
   - Estimated 1-year returns
   - BUY/SELL/RETAIN recommendation
   - Risk assessment

3. **Sector Diversification**
   - Sector-wise allocation
   - Diversification quality
   - Concentration risks

4. **Overall Recommendations**
   - Top holdings to consider selling
   - Top holdings to consider buying more
   - Holdings to retain
   - Rebalancing suggestions

5. **Risk Assessment**
   - Overall portfolio risk level
   - Key risk factors
   - Mitigation strategies

## Requirements

- Holdings data must be imported to database first
- Database connection configured in `input_parsers/db_config.env`
- LangChain and ChatPerplexity configured

## Example Workflow

```bash
# Step 1: Import holdings to database
python save_holdings_to_db.py holdings_files/mf_holdings_1.pdf --create-tables

# Step 2: Analyze holdings
python analyze_holdings_from_db.py --output analysis_report.txt

# Step 3: View analysis
cat analysis_report.txt
```

## Integration with Agentic AI

You can integrate this into your agentic AI workflow:

```python
from analyze_holdings_from_db import HoldingsAnalyzer

# In your agent workflow
analyzer = HoldingsAnalyzer()
analysis = analyzer.analyze_from_db()

# Use analysis in your agent's response
agent_response = f"Based on your portfolio analysis:\n\n{analysis}"
```

