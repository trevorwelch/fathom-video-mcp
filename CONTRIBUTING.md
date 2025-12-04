# Contributing

Thanks for your interest in contributing to fathom-video-mcp!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/fathom-mcp.git
   cd fathom-mcp
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Set your Fathom API key:
   ```bash
   export FATHOM_API_KEY="your-api-key"
   ```

4. Run the server locally:
   ```bash
   uv run python -m fathom_video_mcp.server
   ```

## Making Changes

1. Create a branch for your changes
2. Make your changes
3. Test locally with Claude Code or Claude Desktop
4. Submit a pull request

## Code Style

- Use type hints
- Keep functions focused and simple
- Follow existing patterns in the codebase

## Reporting Issues

Please open an issue on GitHub with:
- What you expected to happen
- What actually happened
- Steps to reproduce
