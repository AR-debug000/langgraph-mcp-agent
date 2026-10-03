import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from rag.retriever import retrieve_documents


# Load environment variables BEFORE creating Claude
load_dotenv()


# Claude
llm = ChatAnthropic(
    model="claude-sonnet-5-5"
)


def rag_agent(question: str) -> str:

    # 1. Search Qdrant
    documents = retrieve_documents(
        question,
        limit=3
    )

    # No relevant documents
    if not documents:
        return "I could not find relevant information in the PDF."

    # 2. Prepare retrieved context
    context_parts = []

    for document in documents:

        context_parts.append(
            f"""
Page: {document['page']}

{document['text']}
"""
        )

    context = "\n\n".join(context_parts)

    # 3. Give retrieved context to Claude
    prompt = f"""
You are a RAG assistant.

Answer the user's question using ONLY the information
provided in the PDF context below.

If the answer is not present in the context,
say that the information was not found in the PDF.

Always mention the relevant page number when possible.

PDF CONTEXT:
----------------
{context}
----------------

USER QUESTION:
{question}
"""

    # 4. Ask Claude
    response = llm.invoke(prompt)

    return response.content
