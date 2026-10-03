import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


mcp = FastMCP("Google Calendar MCP")

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

TOKEN_FILE = "token.json"

MCP_CONFIG = os.path.expanduser(
    r"~/.gemini/config/mcp_config.json"
)


def get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        with open(MCP_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)

        oauth = config["mcpServers"]["calendar"]["oauth"]

        client_config = {
            "web": {
                "client_id": oauth["clientId"],
                "client_secret": oauth["clientSecret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    "http://localhost:8080/"
                ],
            }
        }

        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES
        )

        creds = flow.run_local_server(
            host="localhost",
            port=8080,
            open_browser=True
        )

    with open(TOKEN_FILE, "w", encoding="utf-8") as token:
        token.write(creds.to_json())

    return creds


def get_calendar_service():
    creds = get_credentials()

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


@mcp.tool()
def list_events() -> str:
    """List upcoming Google Calendar events."""

    service = get_calendar_service()

    now = datetime.now(timezone.utc).isoformat()

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = result.get("items", [])

    if not events:
        return "No upcoming calendar events found."

    output = []

    for event in events:
        start = event["start"].get(
            "dateTime",
            event["start"].get("date", "")
        )

        output.append(
            f"ID: {event['id']}\n"
            f"Title: {event.get('summary', 'No title')}\n"
            f"Start: {start}\n"
            f"Description: {event.get('description', '')}"
        )

    return "\n\n".join(output)


@mcp.tool()
def create_event(
    title: str,
    date: str,
    time: str,
    description: str = ""
) -> str:
    """Create a Google Calendar event."""

    service = get_calendar_service()

    pakistan_tz = ZoneInfo("Asia/Karachi")

    start_dt = datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=pakistan_tz)

    end_dt = start_dt.replace(
        minute=start_dt.minute + 30
    )

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Karachi",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Karachi",
        },
    }

    created = (
        service.events()
        .insert(
            calendarId="primary",
            body=event
        )
        .execute()
    )

    return (
        f"Event created successfully.\n"
        f"Title: {created.get('summary')}\n"
        f"Start: {created['start'].get('dateTime')}\n"
        f"Event ID: {created.get('id')}"
    )


@mcp.tool()
def delete_event(event_id: str) -> str:
    """Delete a Google Calendar event using its event ID."""

    service = get_calendar_service()

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return f"Event {event_id} deleted successfully."


@mcp.tool()
def search_events(keyword: str) -> str:
    """Search Google Calendar events."""

    service = get_calendar_service()

    result = (
        service.events()
        .list(
            calendarId="primary",
            q=keyword,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = result.get("items", [])

    if not events:
        return f"No events found for '{keyword}'."

    output = []

    for event in events:
        output.append(
            f"ID: {event['id']} | "
            f"Title: {event.get('summary', 'No title')} | "
            f"Start: {event['start'].get('dateTime', event['start'].get('date', ''))}"
        )

    return "\n".join(output)


if __name__ == "__main__":
    mcp.run()