import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "stdio",
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "ghcr.io/github/github-mcp-server",
                ],
            }
        }
    )

    tools = await client.get_tools()

    print("GitHub MCP connected")
    print("Number of tools:", len(tools))

    for tool in tools:
        print(tool.name)


asyncio.run(main())