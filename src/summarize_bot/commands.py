"""Discord bot commands as standalone functions."""

import discord
from discord import app_commands
import logging
from datetime import datetime, timedelta
from src.summarize_bot.ollama_client import OllamaClient
from src.summarize_bot.discord_tool import get_messages

logger = logging.getLogger(__name__)


def parse_time_range(time_range: str) -> str:
    """Parse time range string to ISO timestamp.
    
    Args:
        time_range: Time range description (e.g., "last day", "last 3 hours", "last week")
    
    Returns:
        ISO 8601 timestamp string
    
    Raises:
        ValueError: If time range is invalid or not recognized
    """
    time_range = time_range.lower().strip()
    
    # Pattern: "last X [hours|days|weeks|minutes]" or "last [hours|days|weeks|minutes]"
    import re
    match = re.match(r'last\s+(\d+)?\s*(hour|day|week|minute)(s?)', time_range, re.IGNORECASE)

    if match:
        amount_str = match.group(1)
        unit = match.group(2).lower()
        is_plural = bool(match.group(3))

        if amount_str:
            amount = int(amount_str)
        else:
            amount = 1

        if unit == 'hour':
            delta = timedelta(hours=amount)
        elif unit == 'day':
            delta = timedelta(days=amount)
        elif unit == 'week':
            delta = timedelta(weeks=amount)
        elif unit == 'minute':
            delta = timedelta(minutes=amount)
        else:
            raise ValueError(f"Unknown time unit: {unit}")

        current_time = datetime.utcnow()
        target_time = current_time - delta
        return target_time.isoformat() + "Z"

    raise ValueError("Invalid time range format. Use 'last X hours', 'last hours', 'last X days', 'last days', 'last X weeks', 'last weeks', 'last X minutes', or 'last minutes'")


def setup_commands(tree: app_commands.CommandTree, ollama_client: OllamaClient):
    """Register all app commands.

    Args:
        tree: The CommandTree to register commands on
        ollama_client: The Ollama client for generating summaries
    """
    @tree.command(name="summarize", description="Summarize messages from the current channel within a time range")
    async def summarize(interaction: discord.Interaction, time_range: str):
        """Summarize messages from the current channel within a time range.

        Args:
            interaction: Discord interaction
            time_range: Time range description (e.g., "last hour", "last 3 hours", "last week")
        """
        # Only respond to users, not bots
        if interaction.user.bot:
            return

        try:
            # Defer interaction response (for potentially long operations)
            await interaction.response.defer(ephemeral=False)

            # Parse time range to ISO timestamp
            timestamp = parse_time_range(time_range)

            # Get channel ID
            channel_id = str(interaction.channel.id)

            # Fetch messages directly (bot handles time parsing now)
            result = await get_messages(interaction.client, channel_id, timestamp)
            messages = result.get("messages", [])

            # Generate summary using LLM
            summary = await ollama_client.summarize_analyze(messages)

            # Edit the deferred response with the summary
            await interaction.edit_original_response(content=f"📋 **Summary of {time_range}**\n\n{summary}")

        except ValueError as e:
            await interaction.followup.send(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            await interaction.followup.send(f"❌ Failed to generate summary: {str(e)}")