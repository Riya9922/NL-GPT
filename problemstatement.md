Problem Statement: AI-Powered Output Evaluation & Improvement Tool
Overview
You are tasked with building an AI-powered evaluation tool that helps users assess the quality, reliability, and completeness of AI-generated responses.
The system appears as an expandable panel alongside AI outputs and enables users to evaluate responses across dimensions such as factual accuracy, source reliability, reasoning quality, missing considerations, and overall answer usefulness.
The tool should intelligently analyze the original AI response, identify strengths and weaknesses, and generate an improved version when requested.

The goal is to help evaluate chatGPT outputs by maintaining transparency around assumptions, uncertainty, and reasoning so they can confidently make decisions. 


Objective
Design and implement a web application that:
Evaluates AI-generated responses across multiple quality dimensions.
Helps users verify claims and understand the reasoning behind outputs.
Identifies missing information, assumptions, and potential limitations.
Provides trustworthy sources and evidence where applicable.
Generates an improved version of the answer based on user-selected evaluation criteria.
Displays findings in a clear and actionable format.

System Workflow
1. Input Collection
Capture:
Original AI response
User query/prompt
Available sources and citations
User-provided context
Conversation memory (if available)
User-selected 5 evaluation criteria:
Claim Verification
Source Transparency
Logic & Reasoning Check
Missing Factors
Improve Answer Quality

 2. Response Analysis Layer
Analyze the AI-generated response by:
Breaking it into individual claims Identifying assumptions
Detecting unsupported statements
Evaluating logical consistency
Assessing completeness
Identifying areas requiring external validation
Output:
{
 "claims": [...],
 "assumptions": [...],
 "reasoning_steps": [...],

3. User Evaluation Preferences
Allow users to select evaluation dimensions:
Claim Verification
Supported Facts
Needs Verification



Sources
Sources Used
☑ Memory
Previous conversations
Saved preferences
☑ User-Provided Context
Uploaded files
Links provided by user
Information in prompt
☑ Web Sources
Blogs
News articles
Websites
☑ Research & Reports
Industry reports
Whitepapers
Academic papers
☑ Company Information
Official company websites
Investor reports
Press releases
☑ Internal Knowledge
Model knowledge not backed by retrieved sources
➕ Add Your Own Source
Reasoning & Assumptions
Reasoning Path
Key Assumptions
What's Missing?
Missing Factors
Improve Answer Quality
Additional information needed
Suggested context inputs
4. Evaluation Engine
Use an LLM to evaluate:
Claim Verification
Which claims are supported?
Which claims are uncertain?
Source Analysis
Are sources trustworthy?
Are important sources missing?
Logic & Reasoning
Does the conclusion follow from the evidence?
Are there logical gaps?
Alternative perspectives
Missing Factors
Answer Quality
Clarity
Completeness
Actionability


5. Regeneration Engine
Using findings from the evaluation layer:
Improve factual accuracy
Add supporting evidence
Address missing considerations
Strengthen reasoning
Increase clarity and usefulness
Generate:
Improved answer
Summary of changes made
.Output Display
Present evaluation results and in an expandable panel next to the AI response.
Facts & Verification
Highlighting text with pastel green coolr and yellow color for verified facts and needs verification respectively. Hovering over it provides sources links max 3 min 1 for verified facts and short reason for needs verification. 
Sources
Sources Used
☑ Memory
Previous conversations
Saved preferences
☑ User-Provided Context
Uploaded files
Links provided by user
Information in prompt
☑ Web Sources
Blogs
News articles
Websites
☑ Research & Reports
Industry reports
Whitepapers
Academic papers
☑ Company Information
Official company websites
Investor reports
Press releases
☑ Internal Knowledge
Model knowledge not backed by retrieved sources
➕ Add Your Own Source

With option to uncheck the box
Reasoning & Assumptions
Conclusion
Reasoning Path - 3-4 logical steps - that arrives from verified sources(hyperlink)
Key Assumptions
Alternate perspectives
Critique 

Example: SNITCH should prioritize opening a store in Bangalore.
Reasoning Path
Demand appears strong.
Existing customer interest is high.
Brand awareness is already established.
Each step can be expandable.
Brand awareness is already established
Expand:
Evidence Used:
- Existing stores in Bangalore
- Social media engagement
- Customer discussions
Example:
GPT says:
Bangalore is likely the strongest market.
Reasoning View:
Assumptions Identified

• Store demand correlates with social media engagement.
• Existing store success predicts future store success.
• Competitor presence does not significantly affect demand.
This is powerful because users often miss hidden assumptions.

What's Missing?
Output
Example Original Answer:
Open another Bangalore store.
What's Missing:
⚠️ Competitor Analysis
No evaluation of nearby competitors.
⚠️ Store Economics
Rent and profitability assumptions not assessed.
⚠️ Cannibalization Risk
Impact on existing Bangalore stores not discussed.
⚠️ Market Saturation
No analysis of remaining demand.
Improve Answer Quality
Recommended inputs
Suggested context additions
Regenerated Answer
Improved response based on selected evaluation preferences

