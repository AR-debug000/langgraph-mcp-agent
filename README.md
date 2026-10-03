# LangGraph MCP Multi-Agent AI System

A multi-agent AI system built with LangGraph, Claude, MCP, RAG, GitHub, Google Calendar, and Email integrations.

## Features

- 🤖 Multi-agent architecture using LangGraph
- 🧠 Claude AI using Anthropic
- 📚 RAG-based question answering from BSCS syllabus PDF
- 🐙 GitHub MCP integration
- 📅 Google Calendar integration
- 📧 Email MCP integration
- 🔀 Supervisor agent for intelligent routing
- 🗄️ Qdrant Cloud vector database
- 🔐 Environment variables for API credentials

## Agents

The system contains four specialist agents:

### 1. RAG Agent

Handles questions related to the uploaded BSCS syllabus PDF.

It uses:

- PDF document
- Text chunking
- HashingVectorizer
- Qdrant Cloud
- Retrieval-Augmented Generation

### 2. GitHub Agent

Handles GitHub-related operations through GitHub MCP.

Examples:

- Get GitHub profile information
- List repositories
- Get repository information
- Work with GitHub-related operations

### 3. Calendar Agent

Handles calendar operations through Google Calendar MCP.

Examples:

- Create calendar events
- List events
- Get event information
- Update events
- Delete events
- Respond to events

### 4. Email Agent

Handles email-related operations through MCP.

Examples:

- Send emails
- List emails
- Search emails

## Architecture

```text
                    User
                      |
                      v
                Supervisor
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
      RAG          GitHub       Calendar
     Agent          Agent         Agent
        |             |             |
        v             v             v
    Qdrant       GitHub MCP   Google Calendar
        |
        |
        +-----------------------------+
                                      |
                                      v
                                  Email Agent
                                      |
                                      v
                                  Email MCP