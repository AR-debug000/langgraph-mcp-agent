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


async def _email_agent(question: str) -> str:

    client = MultiServerMCPClient(
        {
            "email": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    os.path.join(
                        "mcp_custom",
                        "email_mcp.py"
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
                "You are the Email specialist agent. "
                "Use the available Email MCP tools to answer email-related "
                "requests. "
                "Use tools when the user wants to send, list, or search "
                "emails. "
                "Do not invent email information."
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

    return "I could not complete the Email operation."


def email_agent(question: str) -> str:
    return asyncio.run(_email_agent(question))