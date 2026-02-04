# Summarize Bot

A Discord bot that uses an LLM to summarize missed messages in channels. The bot employs an agent-based approach where the LLM decides what messages to fetch using function calling.

## Features

- ✅ Agent-based workflow (LLM decides message fetches)
- ✅ Function calling with Discord query tool
- ✅ `/summarize <time_range>` command
- ✅ Time range parsing (last hour, last 30 minutes, etc.)
- ✅ Context window management with truncation notifications
- ✅ Multiple channel support
- ✅ Configurable via environment variables

## Installation

### Using uv (recommended)

```bash
# Install uv (if not already installed)
pip install uv

# Clone the repository
git clone <repository-url>
cd summarize-bot

# Install dependencies
uv sync

# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
```

## Configuration

Edit `.env` with your settings:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# Ollama Server Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Context Window Configuration
# Adjust based on your model's context window and performance
MAX_CONTEXT_TOKENS=8000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `OLLAMA_URL` | URL of your Ollama server | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name to use | `llama3` |
| `MAX_CONTEXT_TOKENS` | Maximum context window size | `8000` |

## Setting Up Discord Bot

1. Create a new application on [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot in your application
3. Generate a bot token and copy it
4. Invite the bot to your server with the following permissions:
   - `Read Messages/View Channels`
   - `Send Messages`
5. Add the bot to a server and verify it's online

## Usage

### Basic Usage

Use the `/summarize` command in any channel where the bot is present:

```
/summarize last hour
/summarize last 30 minutes
/summarize last 24 hours
```

### Time Ranges

The bot supports the following time range formats:
- `last hour`
- `last 30 minutes`
- `last 6 hours`
- `last 24 hours`
- `last 7 days`

The bot will automatically parse these and fetch messages from the current channel.

## Running the Bot

```bash
# Using uv
uv run python -m summarize_bot

# Or using direct Python
python -m src.summarize_bot
```

## Project Structure

```
summarize-bot/
├── pyproject.toml      # uv configuration
├── src/
│   └── summarize_bot/
│       ├── __init__.py
│       ├── bot.py              # Discord bot main logic
│       ├── ollama_client.py    # Ollama API client
│       ├── discord_tool.py     # Tool for querying Discord messages
│       └── prompt.py           # System prompt and tool definitions
├── .env.example        # Environment variable template
└── README.md           # This file
```

## Architecture

### Components

1. **Bot** (`bot.py`)
   - Discord bot setup using discord.py
   - `/summarize` command handler
   - Time range parsing
   - Integration with Ollama client

2. **Ollama Client** (`ollama_client.py`)
   - HTTP client for Ollama API
   - Function calling support
   - Context window management and truncation

3. **Discord Tool** (`discord_tool.py`)
   - Tool function for LLM to fetch messages
   - Discord API integration

4. **Prompt** (`prompt.py`)
   - System prompt with task instructions
   - Tool definitions for function calling
   - Context limit warnings

### Workflow

1. User runs `/summarize <time_range>` in a channel
2. Bot parses time range into timestamp
3. Bot sends system prompt + LLM with tool definitions
4. LLM decides what messages to fetch
5. LLM calls `get_messages()` tool
6. Tool fetches messages from Discord API
7. Bot truncates messages if they exceed context limits
8. Bot notifies user if truncation occurred
9. Messages are fed back to LLM
10. LLM iteratively fetches more messages if needed
11. LLM generates and returns final summary
12. Bot displays summary to user

## Error Handling

- Invalid time range formats: Returns error message to user
- Discord API errors: Returns error message to user
- Ollama API errors: Returns error message to user
- Context limits: Truncates messages and notifies user

## Development

### Adding Dependencies

Add dependencies to `pyproject.toml` under `dependencies`:

```toml
dependencies = [
    "discord.py>=2.4.0",
    "requests>=2.32.0",
    "python-dotenv>=1.0.0",
    # Add your dependencies here
]
```

Then run:

```bash
uv sync
```

### Code Style

Follow Python best practices:
- Use descriptive variable names
- Keep functions small and focused
- Add docstrings for complex functions
- Use logging for important events

## Troubleshooting

### Bot won't start
- Check that `DISCORD_TOKEN` is set correctly in `.env`
- Verify the bot token has proper permissions

### LLM can't fetch messages
- Ensure Ollama server is running
- Check `OLLAMA_URL` is correct
- Verify the model name exists in Ollama

### Summary is too short
- Increase `MAX_CONTEXT_TOKENS` in `.env`
- Try a shorter time range

### Context limit errors
- Reduce `MAX_CONTEXT_TOKENS` in `.env`
- Use shorter time ranges

## License

This project is provided as-is for educational and personal use.