
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    print("Tavily API key not found!")
else:
    tavily = TavilyClient(api_key=api_key)

    response = tavily.search(
        query="What are the latest developments in generative AI?",
        max_results=3
    )

    print("\n========== TAVILY SEARCH RESULTS ==========")

    for result in response["results"]:
        print("\nTitle:", result["title"])
        print("URL:", result["url"])
        print("Content:", result["content"])

    print("\nTavily Working!")
