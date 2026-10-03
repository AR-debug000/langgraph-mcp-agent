import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()


mcp = FastMCP("github")


@mcp.tool()
def github_token_status() -> str:
    """
    Check whether the GitHub token is configured.
    """

    token = os.getenv("GITHUB_TOKEN")

    if token:
        return "GitHub token is configured."

    return "GitHub token is not configured."


if __name__ == "__main__":
    mcp.run()