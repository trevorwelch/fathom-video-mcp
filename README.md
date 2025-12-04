# Fathom Video MCP Server

An MCP (Model Context Protocol) server that provides access to your [Fathom](https://fathom.video) meeting recordings, AI-generated summaries, and transcripts.

## Features

- **List Meetings** - Browse your Fathom meetings with filtering by date, recorder, or team
- **Get Summaries** - Retrieve AI-generated meeting summaries in markdown format
- **Get Transcripts** - Access full transcripts with speaker attribution and timestamps

## Installation

### Via uvx (recommended)

```bash
uvx fathom-video-mcp
```

### Via pip

```bash
pip install fathom-video-mcp
```

### From source

```bash
git clone https://github.com/your-org/fathom-mcp.git
cd fathom-mcp
uv sync
```

## Configuration

### Step 1: Get your Fathom API Key

1. Go to [fathom.video/api_settings/new](https://fathom.video/api_settings/new) and log in
2. Select **Generate Api Key**
3. Copy your new API key and save it somewhere secure

### Step 2: Add to Claude Code or Claude Desktop

Choose one of the following based on which Claude app you use.

#### Claude Code

Edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "fathom": {
      "command": "uvx",
      "args": ["fathom-video-mcp"],
      "env": {
        "FATHOM_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Claude Desktop

Edit your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fathom": {
      "command": "uvx",
      "args": ["fathom-video-mcp"],
      "env": {
        "FATHOM_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Step 3: Restart Claude

Restart Claude Code or Claude Desktop to load the new MCP server. You should now be able to ask Claude about your Fathom meetings.

## Available Tools

### list_meetings

List your Fathom meetings with optional filters.

**Parameters:**
- `limit` (int, optional): Maximum number of meetings to return (1-50)
- `search` (string, optional): Smart search - matches titles, attendee names, and email domains
- `cursor` (string, optional): Pagination cursor from previous response
- `created_after` (string, optional): ISO timestamp to filter meetings after
- `created_before` (string, optional): ISO timestamp to filter meetings before
- `include_summary` (bool, optional): Include AI summary in response
- `include_transcript` (bool, optional): Include transcript in response
- `include_action_items` (bool, optional): Include action items in response
- `recorded_by` (list[string], optional): Filter by recorder email addresses
- `teams` (list[string], optional): Filter by team names
- `calendar_invitees_domains_type` (string, optional): Filter by invitee type ('all', 'only_internal', 'one_or_more_external')
- `invitee_domains` (list[string], optional): Filter by invitee email domains (e.g., ['acme.com'])

**Example:**
```
List my meetings from the last week
```

### get_summary

Get the AI-generated summary for a specific meeting.

**Parameters:**
- `recording_id` (int, required): The recording ID from list_meetings

**Example:**
```
Get the summary for meeting 123456789
```

### get_transcript

Get the full transcript with speaker attribution.

**Parameters:**
- `recording_id` (int, required): The recording ID from list_meetings

**Example:**
```
Get the transcript for meeting 123456789
```

## Development

### Running locally

```bash
cd fathom-mcp
uv sync
export FATHOM_API_KEY="your-api-key"
uv run python -m fathom_video_mcp.server
```

### Building

```bash
uv build
```

### Publishing to PyPI

```bash
uv publish
```

## License

MIT
