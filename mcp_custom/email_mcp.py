from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Email MCP")


emails = []


@mcp.tool()
def send_email(
    recipient: str,
    subject: str,
    body: str
) -> str:
    """Create and send an email."""

    email = {
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }

    emails.append(email)

    return (
        f"Email sent successfully.\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n"
        f"Body: {body}"
    )


@mcp.tool()
def list_emails() -> str:
    """List emails handled by the Email MCP server."""

    if not emails:
        return "No emails found."

    result = []

    for i, email in enumerate(emails, start=1):
        result.append(
            f"{i}. To: {email['recipient']} | "
            f"Subject: {email['subject']} | "
            f"Body: {email['body']}"
        )

    return "\n".join(result)


@mcp.tool()
def search_emails(keyword: str) -> str:
    """Search emails by recipient, subject, or body."""

    keyword = keyword.lower()

    matches = []

    for email in emails:
        if (
            keyword in email["recipient"].lower()
            or keyword in email["subject"].lower()
            or keyword in email["body"].lower()
        ):
            matches.append(
                f"To: {email['recipient']} | "
                f"Subject: {email['subject']} | "
                f"Body: {email['body']}"
            )

    if not matches:
        return f"No emails found for '{keyword}'."

    return "\n".join(matches)


if __name__ == "__main__":
    mcp.run()