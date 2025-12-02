"""
LLM Analysis Helper Module
Provides improved LLM analysis with iterative refinement, validation, and better prompting
"""
import json
import re
from typing import Dict, List, Optional, Any
from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate


def extract_json_from_response(response: str) -> Optional[Dict]:
    """
    Extract JSON from LLM response, handling markdown code blocks and other formatting
    
    Args:
        response: Raw LLM response string
    
    Returns:
        Parsed JSON dict or None if extraction fails
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Try parsing the entire response
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return None


def validate_analysis_response(data: Dict) -> tuple[bool, List[str]]:
    """
    Validate the structure of LLM analysis response
    
    Args:
        data: Parsed JSON response
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Response is not a dictionary")
        return False, errors
    
    # Check required fields
    required_fields = ['hypotheses', 'overall_confidence', 'needs_follow_up']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate hypotheses structure
    if 'hypotheses' in data:
        if not isinstance(data['hypotheses'], list):
            errors.append("hypotheses must be a list")
        else:
            for i, hyp in enumerate(data['hypotheses']):
                if not isinstance(hyp, dict):
                    errors.append(f"hypothesis {i} is not a dictionary")
                    continue
                
                required_hyp_fields = ['description', 'confidence_score']
                for field in required_hyp_fields:
                    if field not in hyp:
                        errors.append(f"hypothesis {i} missing field: {field}")
                
                # Validate confidence score
                if 'confidence_score' in hyp:
                    try:
                        score = float(hyp['confidence_score'])
                        if not (0.0 <= score <= 1.0):
                            errors.append(f"hypothesis {i} confidence_score out of range: {score}")
                    except (ValueError, TypeError):
                        errors.append(f"hypothesis {i} confidence_score is not a number")
    
    # Validate overall_confidence
    if 'overall_confidence' in data:
        try:
            score = float(data['overall_confidence'])
            if not (0.0 <= score <= 1.0):
                errors.append(f"overall_confidence out of range: {score}")
        except (ValueError, TypeError):
            errors.append("overall_confidence is not a number")
    
    return len(errors) == 0, errors


def create_improved_prompt_template() -> PromptTemplate:
    """
    Create an improved prompt template with better structure and examples
    
    Returns:
        PromptTemplate with enhanced instructions
    """
    template = """You are a senior equity research analyst with 20 years of experience analyzing Indian stock markets.
Your task is to analyze significant price movements in stock holdings and provide well-researched hypotheses about the causes.

IMPORTANT INSTRUCTIONS:
1. Focus on events and news from the last 3-4 days that could explain the price movement
2. Provide 2-5 hypotheses per holding, ranked by likelihood
3. Be specific about dates, events, and sources
4. Confidence scores should reflect ho
w certain you are about the cause (0.0 = uncertain, 1.0 = very certain)
5. Only include hypotheses that are directly relevant to today's price movement

EXAMPLE RESPONSE FORMAT:
{{
  "hypotheses": [
    {{
      "description": "Company announced Q3 results with 25% revenue growth, beating analyst estimates",
      "confidence_score": 0.85,
      "event_date": "2025-01-15",
      "relevance_to_today": true,
      "source": "company_announcement"
    }},
    {{
      "description": "Sector received positive news about government policy changes affecting the industry",
      "confidence_score": 0.60,
      "event_date": "2025-01-14",
      "relevance_to_today": true,
      "source": "news"
    }}
  ],
  "overall_confidence": 0.75,
  "needs_follow_up": false,
  "follow_up_question": ""
}}

Portfolio Data:
{holdings_data}

Analyze each holding and provide your response in the exact JSON format shown above. 
Pay special attention to company names to avoid confusion between similar symbols.
If you cannot find specific reasons, indicate lower confidence scores and suggest follow-up research."""

    return PromptTemplate(
        input_variables=["holdings_data"],
        template=template
    )


def create_self_correction_prompt(original_response: str, errors: List[str]) -> PromptTemplate:
    """
    Create a prompt to ask LLM to correct its previous response
    
    Args:
        original_response: The previous LLM response
        errors: List of validation errors
    
    Returns:
        PromptTemplate for correction
    """
    template = """You previously provided this analysis, but it has some issues that need to be fixed:

ORIGINAL RESPONSE:
{original_response}

VALIDATION ERRORS:
{errors}

Please correct your response to fix these errors. Ensure:
1. The response is valid JSON
2. All required fields are present
3. Confidence scores are between 0.0 and 1.0
4. The structure matches the template exactly

Provide the corrected response in JSON format:"""

    return PromptTemplate(
        input_variables=["original_response", "errors"],
        template=template
    )


def analyze_with_retry(llm: ChatPerplexity, 
                       holdings_data: str,
                       max_retries: int = 3,
                       temperature: float = 0.5) -> Dict[str, Any]:
    """
    Analyze holdings with retry logic and validation
    
    Args:
        llm: ChatPerplexity LLM instance
        holdings_data: JSON string of holdings data
        max_retries: Maximum number of retry attempts
        temperature: Temperature for LLM (lower = more focused)
    
    Returns:
        Validated analysis response dictionary
    """
    # Create improved prompt
    prompt = create_improved_prompt_template()
    chain = LLMChain(llm=llm, prompt=prompt)
    
    for attempt in range(max_retries):
        try:
            # Run analysis
            response = chain.run(holdings_data=holdings_data)
            
            # Extract JSON
            parsed = extract_json_from_response(response)
            
            if parsed is None:
                # JSON extraction failed - use self-correction to fix JSON format
                if attempt < max_retries - 1:
                    print(f"[Attempt {attempt + 1}] Failed to parse JSON, requesting self-correction...")
                    
                    # Create error message for JSON parsing failure
                    json_errors = [
                        "Response is not valid JSON",
                        "Could not extract JSON from response",
                        "Please format your response as valid JSON"
                    ]
                    
                    # Try self-correction to fix JSON format
                    correction_prompt = create_self_correction_prompt(response, json_errors)
                    correction_chain = LLMChain(llm=llm, prompt=correction_prompt)
                    corrected_response = correction_chain.run(
                        original_response=response,
                        errors="\n".join(f"- {e}" for e in json_errors)
                    )
                    
                    # Try to extract corrected JSON
                    corrected_parsed = extract_json_from_response(corrected_response)
                    if corrected_parsed:
                        # Validate the corrected JSON
                        is_valid_corrected, errors_corrected = validate_analysis_response(corrected_parsed)
                        if is_valid_corrected:
                            return corrected_parsed
                        # If JSON is valid but structure is wrong, continue to validation error handling
                        parsed = corrected_parsed
                    else:
                        # Still couldn't parse after correction, continue to next attempt
                        continue
                else:
                    return {
                        "error": "Failed to extract valid JSON after multiple attempts",
                        "raw_response": response
                    }
            
            # Validate structure (only if we have parsed JSON)
            if parsed is not None:
                is_valid, errors = validate_analysis_response(parsed)
                
                if is_valid:
                    return parsed
                else:
                    # Validation failed - use self-correction to fix structure
                    if attempt < max_retries - 1:
                        print(f"[Attempt {attempt + 1}] Validation errors: {errors}")
                        print("Requesting self-correction...")
                        
                        # Try self-correction
                        correction_prompt = create_self_correction_prompt(response, errors)
                        correction_chain = LLMChain(llm=llm, prompt=correction_prompt)
                        corrected_response = correction_chain.run(
                            original_response=response,
                            errors="\n".join(f"- {e}" for e in errors)
                        )
                        
                        # Try to extract corrected JSON
                        corrected_parsed = extract_json_from_response(corrected_response)
                        if corrected_parsed:
                            is_valid_corrected, errors_corrected = validate_analysis_response(corrected_parsed)
                            if is_valid_corrected:
                                return corrected_parsed
                        
                        continue
                    else:
                        return {
                            "error": "Validation failed after multiple attempts",
                            "errors": errors,
                            "response": parsed
                        }
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[Attempt {attempt + 1}] Error: {e}, retrying...")
                continue
            else:
                return {
                    "error": f"Exception occurred: {str(e)}",
                    "attempt": attempt + 1
                }
    
    return {"error": "Max retries exceeded"}


def analyze_holdings_per_symbol(llm: ChatPerplexity,
                                holdings: List[Dict],
                                temperature: float = 0.5) -> Dict[str, Dict]:
    """
    Analyze each holding separately for more focused analysis
    
    Args:
        llm: ChatPerplexity LLM instance
        holdings: List of holding dictionaries
        temperature: Temperature for LLM
    
    Returns:
        Dictionary mapping symbol to analysis result
    """
    results = {}
    
    # Create a focused prompt for single holding analysis
    single_holding_template = """You are a senior equity research analyst analyzing a single stock's price movement.

Stock Information:
Symbol: {symbol}
Company: {company_name}
Yesterday Price: Rs. {yesterday_price}
Today Price: Rs. {today_price}
Price Change: {variation_percent}%
Quantity Held: {quantity}
Value: Rs. {value}

Provide a focused analysis with 2-5 hypotheses explaining this price movement.
Focus on recent events (last 7 days) that could explain the change.

Respond in JSON format:
{{
  "hypotheses": [
    {{
      "description": "<specific reason>",
      "confidence_score": 0.0-1.0,
      "event_date": "YYYY-MM-DD",
      "relevance_to_today": true,
      "source": "<news/announcement/report>"
    }}
  ],
  "overall_confidence": 0.0-1.0,
  "needs_follow_up": true/false,
  "follow_up_question": "<optional>"
}}"""

    single_prompt = PromptTemplate(
        input_variables=["symbol", "company_name", "yesterday_price", "today_price", 
                       "variation_percent", "quantity", "value"],
        template=single_holding_template
    )
    
    single_chain = LLMChain(llm=llm, prompt=single_prompt)
    
    for holding in holdings:
        symbol = holding.get('symbol', 'UNKNOWN')
        try:
            response = single_chain.run(
                symbol=symbol,
                company_name=holding.get('company', symbol),
                yesterday_price=holding.get('yesterday_price', 0),
                today_price=holding.get('price', 0),
                variation_percent=holding.get('variation_percent', 0),
                quantity=holding.get('quantity', 0),
                value=holding.get('value', 0)
            )
            
            parsed = extract_json_from_response(response)
            if parsed:
                is_valid, errors = validate_analysis_response(parsed)
                if is_valid:
                    results[symbol] = parsed
                else:
                    results[symbol] = {"error": "Validation failed", "errors": errors}
            else:
                results[symbol] = {"error": "Failed to parse JSON"}
        
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results


def combine_analyses(per_symbol_results: Dict[str, Dict]) -> Dict:
    """
    Combine individual symbol analyses into a single response
    
    Args:
        per_symbol_results: Dictionary of symbol -> analysis results
    
    Returns:
        Combined analysis in the standard format
    """
    all_hypotheses = []
    total_confidence = 0.0
    needs_follow_up = False
    follow_up_questions = []
    
    for symbol, analysis in per_symbol_results.items():
        if "error" in analysis:
            continue
        
        hypotheses = analysis.get("hypotheses", [])
        for hyp in hypotheses:
            hyp["symbol"] = symbol  # Tag hypothesis with symbol
            all_hypotheses.append(hyp)
        
        total_confidence += analysis.get("overall_confidence", 0.0)
        if analysis.get("needs_follow_up", False):
            needs_follow_up = True
            follow_up = analysis.get("follow_up_question", "")
            if follow_up:
                follow_up_questions.append(f"{symbol}: {follow_up}")
    
    avg_confidence = total_confidence / len(per_symbol_results) if per_symbol_results else 0.0
    
    return {
        "hypotheses": all_hypotheses,
        "overall_confidence": avg_confidence,
        "needs_follow_up": needs_follow_up,
        "follow_up_question": "; ".join(follow_up_questions) if follow_up_questions else ""
    }


def create_follow_up_prompt_template() -> PromptTemplate:
    """
    Create a prompt template for handling follow-up questions
    Includes original analysis and asks LLM to consolidate results
    
    Returns:
        PromptTemplate for follow-up question handling
    """
    template = """You are a senior equity research analyst. You previously provided an analysis, and now need to answer a follow-up question and consolidate the results.

ORIGINAL ANALYSIS:
{original_analysis}

FOLLOW-UP QUESTION:
{follow_up_question}

HOLDINGS DATA (for context):
{holdings_data}

INSTRUCTIONS:
1. Answer the follow-up question based on the holdings data and your original analysis
2. Consolidate your original hypotheses with any new insights from answering the follow-up
3. Update confidence scores if new information changes your assessment
4. If the follow-up reveals new hypotheses, add them to the list
5. If the follow-up confirms existing hypotheses, increase their confidence scores
6. Set needs_follow_up to false after answering (unless a deeper question emerges)

Provide your consolidated analysis in JSON format:
{{
  "hypotheses": [
    {{
      "description": "<reason description - may be from original or new>",
      "confidence_score": 0.0-1.0,
      "event_date": "YYYY-MM-DD",
      "relevance_to_today": true,
      "source": "<type of source>"
    }}
  ],
  "overall_confidence": 0.0-1.0,
  "needs_follow_up": false,
  "follow_up_question": "",
  "follow_up_answer": "<your answer to the follow-up question>"
}}

Consolidate the original analysis with your follow-up answer into a single comprehensive response."""

    return PromptTemplate(
        input_variables=["original_analysis", "follow_up_question", "holdings_data"],
        template=template
    )


def handle_follow_up_question(llm: ChatPerplexity,
                             original_result: Dict[str, Any],
                             follow_up_question: str,
                             holdings_data: str,
                             max_retries: int = 2,
                             temperature: float = 0.5) -> Dict[str, Any]:
    """
    Handle a follow-up question by making another LLM call with original analysis context
    
    Args:
        llm: ChatPerplexity LLM instance
        original_result: The original analysis result dictionary
        follow_up_question: The follow-up question to answer
        holdings_data: JSON string of holdings data for context
        max_retries: Maximum number of retry attempts
        temperature: Temperature for LLM
    
    Returns:
        Consolidated analysis result with original + follow-up merged
    """
    # Check if original result has errors
    if "error" in original_result:
        return original_result
    
    # Validate follow-up question
    if not follow_up_question or not follow_up_question.strip():
        return original_result
    
    # Create follow-up prompt
    follow_up_prompt = create_follow_up_prompt_template()
    follow_up_chain = LLMChain(llm=llm, prompt=follow_up_prompt)
    
    # Convert original result to JSON string for prompt
    original_analysis_json = json.dumps(original_result, indent=2, default=str)
    
    for attempt in range(max_retries):
        try:
            # Run follow-up analysis
            response = follow_up_chain.run(
                original_analysis=original_analysis_json,
                follow_up_question=follow_up_question,
                holdings_data=holdings_data
            )
            
            # Extract JSON
            parsed = extract_json_from_response(response)
            
            if parsed is None:
                if attempt < max_retries - 1:
                    print(f"[Follow-up Attempt {attempt + 1}] Failed to parse JSON, retrying...")
                    continue
                else:
                    # If follow-up fails, return original result
                    print("[WARNING] Follow-up question handling failed, returning original analysis")
                    return original_result
            
            # Validate structure
            is_valid, errors = validate_analysis_response(parsed)
            
            if is_valid:
                # Successfully got consolidated result
                return parsed
            else:
                if attempt < max_retries - 1:
                    print(f"[Follow-up Attempt {attempt + 1}] Validation errors: {errors}, retrying...")
                    continue
                else:
                    # If validation fails, return original result
                    print("[WARNING] Follow-up response validation failed, returning original analysis")
                    return original_result
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[Follow-up Attempt {attempt + 1}] Error: {e}, retrying...")
                continue
            else:
                print(f"[WARNING] Follow-up question handling failed: {e}, returning original analysis")
                return original_result
    
    # If all retries failed, return original
    return original_result

