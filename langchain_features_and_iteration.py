"""
LangChain Features and Iterative LLM Prompting Examples
Demonstrates how to chain LLM outputs and iterate/refine them
"""
from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain, SequentialChain, SimpleSequentialChain
from langchain_classic.prompts import PromptTemplate
from typing import Dict, List


# ============================================================================
# KEY LANGCHAIN FEATURES
# ============================================================================

"""
1. CHAINING - Connect multiple LLM calls
2. MEMORY - Maintain conversation context
3. TOOLS - Integrate external functions/APIs
4. AGENTS - LLM decides which tools to use
5. RETRIEVAL - Connect to vector databases
6. STREAMING - Real-time response generation
7. CALLBACKS - Monitor and log LLM calls
8. TEMPLATES - Reusable prompt templates
9. OUTPUT PARSERS - Structure LLM responses
10. EMBEDDINGS - Convert text to vectors
"""


# ============================================================================
# FEATURE 1: CHAINING - Use output of one LLM as input to another
# ============================================================================

def example_sequential_chain():
    """Chain multiple LLM calls where output of one feeds into the next"""
    
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    
    # Step 1: Generate initial analysis
    analysis_template = """Analyze this portfolio data and provide initial insights:

Portfolio Data:
{holdings_data}

Provide a brief analysis:"""
    
    analysis_prompt = PromptTemplate(
        input_variables=["holdings_data"],
        template=analysis_template
    )
    analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt, output_key="initial_analysis")
    
    # Step 2: Refine the analysis based on initial output
    refine_template = """Take this initial analysis and refine it with more details:

Initial Analysis:
{initial_analysis}

Original Portfolio Data:
{holdings_data}

Provide a refined, comprehensive analysis with specific recommendations."""
    
    refine_prompt = PromptTemplate(
        input_variables=["initial_analysis", "holdings_data"],
        template=refine_template
    )
    refine_chain = LLMChain(llm=llm, prompt=refine_prompt, output_key="refined_analysis")
    
    # Chain them together
    sequential_chain = SequentialChain(
        chains=[analysis_chain, refine_chain],
        input_variables=["holdings_data"],
        output_variables=["initial_analysis", "refined_analysis"],
        verbose=True
    )
    
    return sequential_chain


# ============================================================================
# FEATURE 2: ITERATIVE REFINEMENT - Multiple passes to improve output
# ============================================================================

def iterative_refinement(holdings_data: str, max_iterations: int = 3):
    """
    Iteratively refine LLM output by feeding it back with refinement instructions
    
    Args:
        holdings_data: Portfolio holdings data
        max_iterations: Number of refinement iterations
        
    Returns:
        Final refined analysis
    """
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    
    # Initial analysis prompt
    initial_template = """Analyze this portfolio:

{holdings_data}

Provide a comprehensive analysis."""
    
    initial_prompt = PromptTemplate(
        input_variables=["holdings_data"],
        template=initial_template
    )
    initial_chain = LLMChain(llm=llm, prompt=initial_prompt)
    
    # Refinement prompt (used in iterations)
    refine_template = """Here is the current analysis:

Current Analysis:
{current_analysis}

Original Portfolio Data:
{holdings_data}

Refinement Instructions:
{refinement_instructions}

Please refine the analysis based on the instructions above. Make it more detailed, specific, and actionable."""
    
    refine_prompt = PromptTemplate(
        input_variables=["current_analysis", "holdings_data", "refinement_instructions"],
        template=refine_template
    )
    refine_chain = LLMChain(llm=llm, prompt=refine_prompt)
    
    # Get initial analysis
    current_analysis = initial_chain.run(holdings_data=holdings_data)
    print(f"Iteration 0 (Initial): {len(current_analysis)} characters")
    
    # Iterative refinement
    refinement_instructions = [
        "Add specific buy/sell/hold recommendations for each holding",
        "Include risk assessment and portfolio diversification analysis",
        "Add actionable next steps and portfolio rebalancing suggestions"
    ]
    
    for i in range(min(max_iterations, len(refinement_instructions))):
        current_analysis = refine_chain.run(
            current_analysis=current_analysis,
            holdings_data=holdings_data,
            refinement_instructions=refinement_instructions[i]
        )
        print(f"Iteration {i+1}: {len(current_analysis)} characters")
    
    return current_analysis


# ============================================================================
# FEATURE 3: MULTI-STEP ANALYSIS PIPELINE
# ============================================================================

def multi_step_analysis_pipeline(holdings_data: str):
    """
    Break analysis into multiple specialized steps, then combine
    """
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    
    # Step 1: Risk Analysis
    risk_template = """Analyze the risk profile of this portfolio:

{holdings_data}

Focus on: risk levels, concentration, volatility."""
    risk_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["holdings_data"], template=risk_template),
        output_key="risk_analysis"
    )
    
    # Step 2: Performance Analysis
    performance_template = """Analyze the performance potential of this portfolio:

{holdings_data}

Focus on: expected returns, growth potential, market trends."""
    performance_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["holdings_data"], template=performance_template),
        output_key="performance_analysis"
    )
    
    # Step 3: Recommendations
    recommendations_template = """Based on these analyses, provide recommendations:

Risk Analysis:
{risk_analysis}

Performance Analysis:
{performance_analysis}

Original Portfolio:
{holdings_data}

Provide specific buy/sell/hold recommendations."""
    recommendations_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["risk_analysis", "performance_analysis", "holdings_data"],
            template=recommendations_template
        ),
        output_key="recommendations"
    )
    
    # Combine all steps
    full_chain = SequentialChain(
        chains=[risk_chain, performance_chain, recommendations_chain],
        input_variables=["holdings_data"],
        output_variables=["risk_analysis", "performance_analysis", "recommendations"],
        verbose=True
    )
    
    return full_chain


# ============================================================================
# FEATURE 4: CONDITIONAL ITERATION - Refine based on quality check
# ============================================================================

def conditional_refinement(holdings_data: str, quality_threshold: int = 500):
    """
    Keep refining until output meets quality criteria
    """
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    
    analysis_template = """Analyze this portfolio:

{holdings_data}

Provide a detailed analysis."""
    
    analysis_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["holdings_data"], template=analysis_template)
    )
    
    quality_check_template = """Evaluate this analysis for completeness:

Analysis:
{analysis}

Is this analysis comprehensive? Provide feedback on what's missing."""
    
    quality_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["analysis"], template=quality_check_template)
    )
    
    refine_template = """Improve this analysis based on feedback:

Current Analysis:
{analysis}

Feedback:
{feedback}

Original Data:
{holdings_data}

Provide an improved, more comprehensive analysis."""
    
    refine_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["analysis", "feedback", "holdings_data"],
            template=refine_template
        )
    )
    
    # Initial analysis
    analysis = analysis_chain.run(holdings_data=holdings_data)
    iteration = 0
    max_iterations = 3
    
    while len(analysis) < quality_threshold and iteration < max_iterations:
        feedback = quality_chain.run(analysis=analysis)
        analysis = refine_chain.run(
            analysis=analysis,
            feedback=feedback,
            holdings_data=holdings_data
        )
        iteration += 1
        print(f"Iteration {iteration}: {len(analysis)} characters")
    
    return analysis


# ============================================================================
# FEATURE 5: PROMPT TEMPLATE VARIATIONS - Try different approaches
# ============================================================================

def prompt_variation_experiment(holdings_data: str):
    """
    Generate multiple variations and combine best parts
    """
    llm = ChatPerplexity(model="sonar", temperature=0.7)
    
    # Variation 1: Detailed analysis
    detailed_template = """Provide a VERY DETAILED analysis of this portfolio:

{holdings_data}

Be extremely thorough and specific."""
    
    # Variation 2: Concise summary
    concise_template = """Provide a CONCISE summary of this portfolio:

{holdings_data}

Be brief but comprehensive."""
    
    # Variation 3: Action-oriented
    action_template = """Provide ACTIONABLE recommendations for this portfolio:

{holdings_data}

Focus on what to do next."""
    
    chains = [
        LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["holdings_data"], template=detailed_template)),
        LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["holdings_data"], template=concise_template)),
        LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["holdings_data"], template=action_template))
    ]
    
    results = []
    for i, chain in enumerate(chains):
        result = chain.run(holdings_data=holdings_data)
        results.append(result)
        print(f"Variation {i+1}: {len(result)} characters")
    
    # Combine best parts
    combine_template = """Combine these different analyses into one comprehensive report:

Detailed Analysis:
{detailed}

Concise Summary:
{concise}

Action Items:
{action}

Create a unified, comprehensive analysis that incorporates the best of each approach."""
    
    combine_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["detailed", "concise", "action"],
            template=combine_template
        )
    )
    
    final = combine_chain.run(
        detailed=results[0],
        concise=results[1],
        action=results[2]
    )
    
    return final


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example holdings data
    sample_holdings = """
    Symbol: AAPL, Value: 10000, Sector: Technology
    Symbol: MSFT, Value: 8000, Sector: Technology
    Symbol: GOOGL, Value: 6000, Sector: Technology
    """
    
    print("=" * 80)
    print("EXAMPLE 1: Sequential Chain")
    print("=" * 80)
    sequential = example_sequential_chain()
    result = sequential.run(holdings_data=sample_holdings)
    print(result)
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Iterative Refinement")
    print("=" * 80)
    refined = iterative_refinement(sample_holdings, max_iterations=2)
    print(refined)
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Multi-Step Pipeline")
    print("=" * 80)
    pipeline = multi_step_analysis_pipeline(sample_holdings)
    result = pipeline.run(holdings_data=sample_holdings)
    print(result)

