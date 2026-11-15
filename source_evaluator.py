
from urllib.parse import urlparse


# Domains that may provide primary information
PRIMARY_DOMAINS = [
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "blog.google",
    "ai.google.dev",
    "deepseek.com",
    "microsoft.com",
    "nvidia.com",
    "arxiv.org",
    "nist.gov"
]


# Domains commonly hosting secondary or user-generated content
SECONDARY_DOMAINS = [
    "medium.com",
    "futureagi.com",
    "masterofcode.com",
    "dataforest.ai",
    "edureka.co"
]
# Research institutions and academic repositories
RESEARCH_DOMAINS = [
    "hai.stanford.edu",
    "stanford.edu",
    "mit.edu",
    "acm.org",
    "ieee.org"
]

def get_source_type(url):

    domain = urlparse(url).netloc.lower()

    # Remove www. if present
    if domain.startswith("www."):
        domain = domain[4:]

    # Check potential primary sources
    for trusted_domain in PRIMARY_DOMAINS:
        if domain == trusted_domain or domain.endswith("." + trusted_domain):
            return "Potential Primary Source"

    # Check research and institutional sources
    for research_domain in RESEARCH_DOMAINS:
        if domain == research_domain or domain.endswith("." + research_domain):
            return "Research / Institutional Source"

    # Check secondary sources
    for secondary_domain in SECONDARY_DOMAINS:
        if domain == secondary_domain or domain.endswith("." + secondary_domain):
            return "Secondary / Commentary Source"

    if domain == "youtube.com" or domain.endswith(".youtube.com"):
        return "Video Source"

    return "Unknown Source"

    domain = urlparse(url).netloc.lower()

    # Remove www. if present
    if domain.startswith("www."):
        domain = domain[4:]

    for trusted_domain in PRIMARY_DOMAINS:

        if domain == trusted_domain or domain.endswith("." + trusted_domain):
            return "Potential Primary Source"

    for secondary_domain in SECONDARY_DOMAINS:

        if domain == secondary_domain or domain.endswith("." + secondary_domain):
            return "Secondary / Commentary Source"

    if "youtube.com" in domain:
        return "Video Source"

    return "Unknown Source"


def evaluate_sources(results):

    evaluated_sources = []

    for index, result in enumerate(results, start=1):

        url = result.get("url", "")
        content = result.get("content", "")
        title = result.get("title", "")

        source_type = get_source_type(url)

        evaluated_sources.append({
            "source_id": f"S{index}",
            "title": title,
            "url": url,
            "content": content,
            "source_type": source_type,
            "search_relevance": result.get("score"),
            "has_content": bool(content.strip())
        })

    return evaluated_sources
