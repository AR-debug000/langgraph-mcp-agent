import os
import base64
from email.mime.text import MIMEText

from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


mcp = FastMCP("Gmail MCP")

TOKEN_FILE = "gmail_token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


@mcp.tool()
def send_email(
    recipient: str,
    subject: str,
    body: str
) -> str:
    """Send a real email through Gmail."""

    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = recipient
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={"raw": raw_message}
        )
        .execute()
    )

    return (
        f"Email sent successfully through Gmail.\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n"
        f"Message ID: {result.get('id')}"
    )


if __name__ == "__main__":
    mcp.run()