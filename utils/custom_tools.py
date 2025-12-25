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


from langchain_community.utilities import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///../assets/Chinook.db")

@tool
def run_sql_query(query: str) -> str:
    """
    Execute a SQL query against the Chinook SQLite database.

    This tool runs a read-only SQL query on the Chinook database and
    returns the result as a string. It is intended for retrieving
    information such as records, aggregates, or filtered data.
    Any execution errors are caught and returned as error messages.

    Args:
        query (str): A valid SQL query to execute against the database.
            The query should be compatible with SQLite syntax.

    Returns:
        str: The query result as a string if execution is successful.
        If an error occurs, a string describing the error is returned.

    Examples:
        >>> run_sql_query("SELECT * FROM Artist LIMIT 5;")
        '[(1, "AC/DC"), (2, "Accept"), ...]'

        >>> run_sql_query("SELECT COUNT(*) FROM Track;")
        '[(3503,)]'
    """
    try:
        return db.run(query)
    except Exception as e:
        return f"Error: {e}"