from dotenv import load_dotenv

load_dotenv(override=True)

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get

mcp = FastMCP("mcp_server")
tavily_client = TavilyClient()

# tool for searching the web
@mcp.tool()
def web_search(query: str) -> Dict[str, Any]:
    """
    Search the public web for up-to-date or external information.

    Use this tool when the question:
    - Requires current or real-world information
    - Cannot be answered reliably from general knowledge
    - Involves recent events, companies, people, or statistics

    Do NOT use this tool if:
    - The answer can be inferred from reasoning or prior context
    - The question is purely conversational or opinion-based

    Args:
        query (str): A concise search query describing the information needed.
            The query should contain the key terms necessary to retrieve relevant results.

    Returns:
        Dict[str, Any]: A dictionary containing search results returned by the
        Tavily search API. The response typically includes:
            - results (List[Dict[str, Any]]): A list of search result entries.
            - Each result may contain fields such as title, content, url, and score.
            - Additional metadata depending on the search response.

    Notes:
        - This tool retrieves external information and may introduce latency.
        - The returned content should be summarized or synthesized before
          being presented to the user.
        - When this tool is used, output ONLY a valid tool call without
          additional natural language text.
    """
    print(f"web_search tool was called with query : {query}\n")
    return tavily_client.search(query)


# Resources - provide access to langchain-ai repo files
@mcp.resource("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """
    Resource for accessing langchain-ai/langchain-mcp-adapters/README.md file

    """
    url = f"https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md"
    try:
        resp = get(url)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"

# Prompt template
@mcp.prompt()
def prompt():
    """Analyze data from a langchain-ai repo file with comprehensive insights"""
    return """
    You are a helpful assistant that answers user questions about LangChain, LangGraph and LangSmith.

    You can use the following tools/resources to answer user questions:
    - search_web: Search the web for information
    - github_file: Access the langchain-ai repo files

    If the user asks a question that is not related to LangChain, LangGraph or LangSmith, you should say "I'm sorry, I can only answer questions about LangChain, LangGraph and LangSmith."

    You may try multiple tool and resource calls to answer the user's question.

    You may also ask clarifying questions to the user to better understand their question.
    """

if __name__ == "__main__":
    mcp.run(transport="stdio")

