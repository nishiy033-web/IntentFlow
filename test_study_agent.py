
from agents.study_agent import run_study_agent


response = run_study_agent(
    subject="DBMS",
    duration="5 days",
    task="Prepare for my DBMS internal examination"
)

if response:
    print("\n========== STUDY AGENT ==========")
    print(response)
    print("\nStudy Agent Working!")
else:
    print("\nStudy Agent Failed!")
