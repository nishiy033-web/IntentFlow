
import os
from dotenv import load_dotenv
from tavily import TavilyClient

from ai_engine import generate_routed_response
from source_evaluator import evaluate_sources


def run_research_agent(task, conversation_history=""):

    load_dotenv()

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Tavily API key not found!"

    tavily = TavilyClient(api_key=api_key)

    # Step 1: Search the web
    search_results = tavily.search(
    query=f"{task}. Prioritise official announcements, primary research, "
          "original reports and authoritative documentation.",
    search_depth="advanced",
    max_results=10,
    include_domains=[
        "openai.com",
        "anthropic.com",
        "deepmind.google",
        "blog.google",
        "ai.google.dev",
        "deepseek.com",
        "microsoft.com",
        "nvidia.com",
        "arxiv.org",
        "nist.gov",
        "hai.stanford.edu",
        "stanford.edu",
        "mit.edu",
        "acm.org",
        "ieee.org"
    ],
    include_domains_mode="prefer"
)

    results = search_results.get("results", [])

    if not results:
        return "No relevant search results found."
    evaluated_sources = evaluate_sources(results)

    # Step 2: Prepare evaluated search context
    research_context = ""

    for source in evaluated_sources:

        research_context += f"""
[{source["source_id"]}]
Title: {source["title"]}
URL: {source["url"]}
Source type: {source["source_type"]}
Tavily relevance score: {source["search_relevance"]}
Content: {source["content"]}

-----------------------------------
"""
    # Step 3: Ask Gemini to analyse the results
    prompt = f"""
You are IntentFlow's specialised Research Agent.

Your task is to produce accurate, evidence-based research.

Previous conversation:
{conversation_history if conversation_history else "No previous conversation."}

Current research task:
{task}

Web search results:
{research_context}

STRICT RESEARCH RULES:

1. Use the provided search results as your primary evidence.

2. Prioritise sources labelled "Potential Primary Source"
   for official announcements, technical documentation,
   original research and statistics.

3. Treat "Secondary / Commentary Source" as supporting
   context, not definitive evidence for important factual claims.

4. Sources labelled "Unknown Source" must be treated cautiously.
   Do not assume they are trustworthy.

5. A source's domain classification does not automatically
   guarantee its reliability. Evaluate whether its actual
   content supports the claim.
   5A. Verify the exact meaning of every statistic before using it.
    Preserve its original population, geography, timeframe,
    measurement and context.

    Never convert:
    - Survey interest into actual adoption.
    - Assessment into active deployment.
    - Correlation into causation.
    - A percentage of respondents into a percentage
      of all organisations.

    If the source does not explicitly support the exact claim,
    do not present that claim as verified.

6. Tavily relevance scores indicate search relevance,
   NOT factual accuracy or source reliability.

7. Every important factual claim must include a source ID.
   Example: [S1]

8. Never invent facts, statistics, dates, model names
   or announcements.

9. Clearly distinguish between:
   - Confirmed facts
   - Predictions and forecasts
   - Opinions and industry expectations

10. If sources disagree or evidence is insufficient,
    clearly mention the uncertainty.

11. Do not present a specific statistic or announcement
    as confirmed when it is supported only by weak or
    unverified secondary sources.

12. If no suitable primary sources are available,
    explicitly mention that the research relies mainly
    on secondary sources.

RESPONSE FORMAT:

## Research Overview
Briefly introduce the topic.

## Key Findings
Explain the most important findings with source IDs.

## Important Trends
Discuss relevant developments and their implications.

## Limitations and Uncertainties
Mention missing, conflicting or insufficient evidence.

## Sources
List the source IDs with their corresponding URLs.

Research should be clear, structured and beginner-friendly.
"""

    return generate_routed_response(
    prompt=prompt,
    intent="research"
)