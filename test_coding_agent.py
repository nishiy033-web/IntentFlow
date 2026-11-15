
from agents.coding_agent import run_coding_agent

response = run_coding_agent(
    task="Explain recursion in Python with a simple example.",
    subject="Python"
)

if response:
    print("\n========== CODING AGENT ==========")
    print(response)
    print("\nCoding Agent Working!")
else:
    print("\nCoding Agent Failed!")
