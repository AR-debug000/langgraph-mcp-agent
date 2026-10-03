import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


llm = ChatAnthropic(
    model="claude-sonnet-5-5"
)


async def _calendar_agent(question: str) -> str:

    client = MultiServerMCPClient(
        {
            "calendar": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    os.path.join(
                        "mcp_custom",
                        "calendar_mcp.py"
                    )
                ],
            }
        }
    )

    tools = await client.get_tools()

    model = llm.bind_tools(tools)

    messages = [
        SystemMessage(
            content=(
                "You are the Calendar specialist agent. "
                "Use the available Calendar MCP tools to answer calendar "
                "related requests. "
                "Use tools when the user wants to create, list, or delete "
                "calendar events. "
                "Do not invent calendar information."
            )
        ),
        HumanMessage(content=question),
    ]

    for _ in range(5):

        response = await model.ainvoke(messages)

        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:

            tool = next(
                (
                    available_tool
                    for available_tool in tools
                    if available_tool.name == tool_call["name"]
                ),
                None,
            )

            if tool is None:
                messages.append(
                    ToolMessage(
                        content=f"Tool not found: {tool_call['name']}",
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

            tool_result = await tool.ainvoke(tool_call["args"])

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return "I could not complete the Calendar operation."


def calendar_agent(question: str) -> str:
    return asyncio.run(_calendar_agent(question))