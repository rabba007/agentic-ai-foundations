from dotenv import load_dotenv

load_dotenv(override=True)

from langchain.tools import tool
from typing_extensions import Dict, Any
from tavily import TavilyClient

tavily_client = TavilyClient()

@tool
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
    return tavily_client.search(query)


system_prompt = """

You are a personal chef. The user will give you a list of ingredients they have left over in their house.

Using the web search tool, search the web for recipes that can be made with the ingredients they have.

Return recipe suggestions and eventually the recipe instructions to the user, if requested.

"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

agent = create_agent(
    model=init_chat_model("llama-3.1-8b-instant", model_provider="groq"),
    tools=[web_search],
    system_prompt=system_prompt
)