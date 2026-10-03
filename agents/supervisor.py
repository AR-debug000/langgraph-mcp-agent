from typing import TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph

from agents.rag_agent import rag_agent
from agents.github_agent import github_agent
from agents.calendar_agent import calendar_agent
from agents.email_agent import email_agent


load_dotenv()


# --------------------------------------------------
# State
# --------------------------------------------------

class AgentState(TypedDict):
    question: str
    route: str
    answer: str


# --------------------------------------------------
# Claude
# --------------------------------------------------

llm = ChatAnthropic(
    model="claude-sonnet-5-5"
)


# --------------------------------------------------
# Supervisor
# --------------------------------------------------

def supervisor_node(state: AgentState):

    question = state["question"]

    prompt = f"""
You are the supervisor of a multi-agent system.

Decide which agent should handle the user's question.

Available agents:

1. rag
   - Questions about information contained in the uploaded PDF
   - Questions about the BSCS syllabus

2. github
   - GitHub repositories
   - GitHub issues
   - GitHub code
   - GitHub commits
   - GitHub pull requests
   - GitHub profile information

3. calendar
   - Calendar events
   - Meetings
   - Creating calendar events
   - Listing calendar events
   - Deleting calendar events

4. email
   - Sending emails
   - Listing emails
   - Searching emails
   - Email-related operations

Return ONLY one of:

rag
github
calendar
email

User question:
{question}
"""

    response = llm.invoke(prompt)

    route = response.content.strip().lower()

    # Safety fallback
    if route not in ["rag", "github", "calendar", "email"]:
        route = "rag"

    return {
        "route": route
    }


# --------------------------------------------------
# RAG Agent
# --------------------------------------------------

def rag_node(state: AgentState):

    answer = rag_agent(
        state["question"]
    )

    return {
        "answer": answer
    }


# --------------------------------------------------
# GitHub Agent
# --------------------------------------------------

def github_node(state: AgentState):

    answer = github_agent(
        state["question"]
    )

    return {
        "answer": answer
    }


# --------------------------------------------------
# Calendar Agent
# --------------------------------------------------

def calendar_node(state: AgentState):

    answer = calendar_agent(
        state["question"]
    )

    return {
        "answer": answer
    }


# --------------------------------------------------
# Email Agent
# --------------------------------------------------

def email_node(state: AgentState):

    answer = email_agent(
        state["question"]
    )

    return {
        "answer": answer
    }


# --------------------------------------------------
# Router
# --------------------------------------------------

def route_agent(state: AgentState):

    return state["route"]


# --------------------------------------------------
# Build Graph
# --------------------------------------------------

builder = StateGraph(AgentState)


builder.add_node(
    "supervisor",
    supervisor_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "github",
    github_node
)

builder.add_node(
    "calendar",
    calendar_node
)

builder.add_node(
    "email",
    email_node
)


# --------------------------------------------------
# START → Supervisor
# --------------------------------------------------

builder.add_edge(
    START,
    "supervisor"
)


# --------------------------------------------------
# Supervisor → Selected Agent
# --------------------------------------------------

builder.add_conditional_edges(
    "supervisor",
    route_agent,
    {
        "rag": "rag",
        "github": "github",
        "calendar": "calendar",
        "email": "email",
    }
)


# --------------------------------------------------
# Agents → END
# --------------------------------------------------

builder.add_edge(
    "rag",
    END
)

builder.add_edge(
    "github",
    END
)

builder.add_edge(
    "calendar",
    END
)

builder.add_edge(
    "email",
    END
)


# --------------------------------------------------
# Compile
# --------------------------------------------------

graph = builder.compile()