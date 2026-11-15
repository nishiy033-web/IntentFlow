
from agents.research_agent import run_research_agent


response = run_research_agent(
    task="Research the latest developments in Generative AI in 2026."
)

if response:
    print("\n========== RESEARCH AGENT ==========")
    print(response)
    print("\nResearch Agent Working!")
else:
    print("\nResearch Agent Failed!")
