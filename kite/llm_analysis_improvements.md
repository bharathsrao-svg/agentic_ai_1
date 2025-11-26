# LLM Analysis Improvement Strategies

## 1. **Iterative Refinement with Validation**
- Parse JSON response and validate structure
- If invalid JSON or missing required fields, retry with a corrected prompt
- Use a "self-correction" prompt that asks the LLM to fix its own output

## 2. **Multi-Step Chain-of-Thought Analysis**
Break down into sequential steps:
- Step 1: Identify significant price movements
- Step 2: Research potential causes for each movement
- Step 3: Evaluate confidence and relevance
- Step 4: Synthesize final hypotheses

## 3. **Few-Shot Learning with Examples**
Include 2-3 example responses in the prompt showing:
- Good hypothesis structure
- Appropriate confidence scores
- Relevant event dates
- Proper source attribution

## 4. **Temperature and Model Tuning**
- Start with lower temperature (0.3-0.5) for more focused responses
- If results are too generic, increase to 0.7-0.9 for more creative analysis
- Try different models: "sonar", "sonar-pro", "llama-3.1-sonar-large-128k-online"

## 5. **Structured Output with Retry Logic**
- Use JSON schema validation
- Retry up to 3 times with progressively clearer instructions
- Fallback to simpler format if JSON parsing fails

## 6. **Context Enhancement**
Add more context to prompts:
- Market indices performance (Nifty, Sensex)
- Sector-specific trends
- Recent news keywords
- Trading volume changes
- Historical price patterns

## 7. **Parallel Analysis per Holding**
- Analyze each holding separately in parallel
- Aggregate results
- Reduces token limits and improves focus

## 8. **Self-Consistency Checks**
- Generate multiple responses
- Compare and find consensus
- Flag disagreements for human review

## 9. **Prompt Engineering Techniques**
- Use role-playing: "You are a senior equity research analyst..."
- Add constraints: "Focus on events in the last 7 days"
- Request reasoning: "Explain your reasoning before providing hypotheses"
- Use formatting hints: "Use bullet points for each hypothesis"

## 10. **Feedback Loop with Confidence Thresholds**
- If overall_confidence < 0.5, ask for more research
- If needs_follow_up is true, generate follow-up questions
- Chain follow-up questions as separate LLM calls

## 11. **Output Post-Processing**
- Extract and validate JSON from markdown code blocks
- Clean up common formatting issues
- Normalize confidence scores
- Validate dates are recent and relevant

## 12. **Hybrid Approach: Summary + Detailed Analysis**
- First call: Quick summary of all movements
- Second call: Deep dive into top 3-5 most significant movements
- Combine results for comprehensive analysis

