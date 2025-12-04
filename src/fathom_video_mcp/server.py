"""Fathom Video MCP Server - Access meeting recordings, summaries, and transcripts."""

import os
from typing import Annotated, Optional

import httpx
from fastmcp import FastMCP

FATHOM_API_BASE = "https://api.fathom.ai/external/v1"

mcp = FastMCP(
    name="fathom-video-mcp",
    instructions="""Fathom Video MCP Server provides access to Fathom meeting recordings.

Available tools:
- list_meetings: List meetings with optional filtering by date, recorder, or team
- get_summary: Get the AI-generated summary for a specific meeting
- get_transcript: Get the full transcript with speaker attribution and timestamps

The recording_id from list_meetings is used to fetch summaries and transcripts.""",
)


def get_api_key() -> str:
    """Get the Fathom API key from environment."""
    api_key = os.environ.get("FATHOM_API_KEY")
    if not api_key:
        raise ValueError(
            "FATHOM_API_KEY environment variable is required. "
            "Get your API key from Fathom settings."
        )
    return api_key


def make_request(endpoint: str, params: dict | None = None) -> dict:
    """Make an authenticated request to the Fathom API."""
    url = f"{FATHOM_API_BASE}{endpoint}"
    headers = {"X-Api-Key": get_api_key()}

    transport = httpx.HTTPTransport(retries=3)
    with httpx.Client(transport=transport, timeout=30.0) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def normalize_search(text: str) -> str:
    """Normalize text for fuzzy matching: lowercase, remove spaces, strip trailing 's'."""
    normalized = text.lower().replace(" ", "").replace("-", "").replace("_", "")
    # Strip trailing 's' to handle simple plurals (labs -> lab, meetings -> meeting)
    if normalized.endswith("s") and len(normalized) > 2:
        normalized = normalized[:-1]
    return normalized


def meeting_matches_search(meeting: dict, search_normalized: str) -> bool:
    """Check if a meeting matches the search term in title, attendees, or emails."""
    # Check title
    title = normalize_search(meeting.get("title") or "")
    if search_normalized in title:
        return True

    # Check meeting_title
    meeting_title = normalize_search(meeting.get("meeting_title") or "")
    if search_normalized in meeting_title:
        return True

    # Check attendee names and emails
    for invitee in meeting.get("calendar_invitees") or []:
        name = normalize_search(invitee.get("name") or "")
        email = (invitee.get("email") or "").lower()
        if search_normalized in name or search_normalized in email:
            return True

    return False


@mcp.tool
def list_meetings(
    limit: Annotated[
        Optional[int], "Maximum number of meetings to return (1-50)"
    ] = None,
    search: Annotated[
        Optional[str], "Smart search: matches titles, attendee names, and email domains (e.g., 'Acme' finds acme.com)"
    ] = None,
    cursor: Annotated[Optional[str], "Pagination cursor from previous response"] = None,
    created_after: Annotated[
        Optional[str], "Filter meetings created after this ISO timestamp (e.g., 2025-01-01T00:00:00Z)"
    ] = None,
    created_before: Annotated[
        Optional[str], "Filter meetings created before this ISO timestamp (e.g., 2025-12-31T23:59:59Z)"
    ] = None,
    include_summary: Annotated[
        bool, "Include AI-generated summary in the response"
    ] = False,
    include_transcript: Annotated[
        bool, "Include full transcript in the response"
    ] = False,
    include_action_items: Annotated[
        bool, "Include action items in the response"
    ] = False,
    recorded_by: Annotated[
        Optional[list[str]], "Filter by email addresses of users who recorded the meetings"
    ] = None,
    teams: Annotated[
        Optional[list[str]], "Filter by team names"
    ] = None,
    calendar_invitees_domains_type: Annotated[
        Optional[str], "Filter by invitee type: 'all', 'only_internal', or 'one_or_more_external'"
    ] = None,
    invitee_domains: Annotated[
        Optional[list[str]], "Filter by invitee email domains (e.g., ['acme.com', 'example.com'])"
    ] = None,
) -> dict:
    """List Fathom meetings with optional filtering.

    Returns a paginated list of meetings. Use the recording_id from the results
    to fetch summaries or transcripts with get_summary or get_transcript.
    """
    # Apply sensible defaults for limit
    if limit is not None:
        limit = max(1, min(50, limit))  # Clamp between 1 and 50

    params = {}

    if cursor is not None:
        params["cursor"] = cursor
    if created_after is not None:
        params["created_after"] = created_after
    if created_before is not None:
        params["created_before"] = created_before
    if include_summary:
        params["include_summary"] = "true"
    if include_transcript:
        params["include_transcript"] = "true"
    if include_action_items:
        params["include_action_items"] = "true"
    if recorded_by is not None:
        params["recorded_by"] = recorded_by
    if teams is not None:
        params["teams"] = teams
    if calendar_invitees_domains_type is not None:
        params["calendar_invitees_domains_type"] = calendar_invitees_domains_type
    if invitee_domains is not None:
        params["calendar_invitees_domains[]"] = invitee_domains

    data = make_request("/meetings", params)

    # Get items and apply client-side filters
    items = data.get("items", [])

    # Smart search: match against titles, attendee names, and emails
    if search:
        search_normalized = normalize_search(search)
        items = [m for m in items if meeting_matches_search(m, search_normalized)]

    # Apply limit after filtering
    if limit is not None:
        items = items[:limit]

    # Format meetings for response
    meetings = []
    for meeting in items:
        meeting_data = {
            "title": meeting.get("title"),
            "meeting_title": meeting.get("meeting_title"),
            "recording_id": meeting.get("recording_id"),
            "url": meeting.get("url"),
            "share_url": meeting.get("share_url"),
            "created_at": meeting.get("created_at"),
            "scheduled_start_time": meeting.get("scheduled_start_time"),
            "scheduled_end_time": meeting.get("scheduled_end_time"),
            "recording_start_time": meeting.get("recording_start_time"),
            "recording_end_time": meeting.get("recording_end_time"),
            "transcript_language": meeting.get("transcript_language"),
        }

        recorded_by_data = meeting.get("recorded_by")
        if recorded_by_data:
            meeting_data["recorded_by"] = {
                "name": recorded_by_data.get("name"),
                "email": recorded_by_data.get("email"),
            }

        invitees = meeting.get("calendar_invitees")
        if invitees:
            meeting_data["calendar_invitees"] = [
                {
                    "name": inv.get("name"),
                    "email": inv.get("email"),
                    "is_external": inv.get("is_external"),
                }
                for inv in invitees
            ]

        summary = meeting.get("default_summary")
        if include_summary and summary:
            meeting_data["summary"] = {
                "template_name": summary.get("template_name"),
                "markdown_formatted": summary.get("markdown_formatted"),
            }

        transcript = meeting.get("transcript")
        if include_transcript and transcript:
            meeting_data["transcript"] = [
                {
                    "speaker": seg.get("speaker", {}).get("display_name", "Unknown"),
                    "text": seg.get("text"),
                    "timestamp": seg.get("timestamp"),
                }
                for seg in transcript
            ]

        action_items = meeting.get("action_items")
        if include_action_items and action_items:
            meeting_data["action_items"] = [
                {
                    "description": item.get("description"),
                    "completed": item.get("completed"),
                    "recording_timestamp": item.get("recording_timestamp"),
                }
                for item in action_items
            ]

        meetings.append(meeting_data)

    return {
        "meetings": meetings,
        "count": len(meetings),
        "next_cursor": data.get("next_cursor"),
    }


@mcp.tool
def get_summary(
    recording_id: Annotated[int, "The recording ID of the meeting (from list_meetings)"],
) -> dict:
    """Get the AI-generated summary for a specific meeting recording.

    Returns a markdown-formatted summary of the meeting including key points
    and discussion topics.
    """
    data = make_request(f"/recordings/{recording_id}/summary")

    summary = data.get("summary")
    if summary:
        return {
            "recording_id": recording_id,
            "template_name": summary.get("template_name"),
            "markdown_formatted": summary.get("markdown_formatted"),
        }

    return {
        "recording_id": recording_id,
        "error": "No summary available for this recording",
    }


@mcp.tool
def get_transcript(
    recording_id: Annotated[int, "The recording ID of the meeting (from list_meetings)"],
) -> dict:
    """Get the full transcript for a specific meeting recording.

    Returns timestamped transcript segments with speaker attribution.
    Each segment includes the speaker name, what they said, and when.
    """
    data = make_request(f"/recordings/{recording_id}/transcript")

    transcript = data.get("transcript", [])
    segments = []
    for seg in transcript:
        segment_data = {
            "text": seg.get("text", ""),
            "timestamp": seg.get("timestamp"),
        }
        speaker = seg.get("speaker")
        if speaker:
            segment_data["speaker"] = {
                "display_name": speaker.get("display_name", "Unknown"),
                "email": speaker.get("matched_calendar_invitee_email"),
            }
        segments.append(segment_data)

    return {
        "recording_id": recording_id,
        "transcript": segments,
        "segment_count": len(segments),
    }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
