"""Discord tool for fetching messages."""

import discord
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


async def get_messages(bot: discord.Client, channel_id: str, since_timestamp: str) -> Dict[str, Any]:
    """
    Fetch messages from a Discord channel since a specific timestamp.

    Args:
        bot: The Discord client instance
        channel_id: The ID of the Discord channel
        since_timestamp: ISO 8601 timestamp (e.g., "2024-01-01T00:00:00Z")

    Returns:
        Dict with "messages" key containing list of message dicts
    """
    try:
        # Parse channel ID
        channel = discord.utils.get(bot.get_all_channels(), id=int(channel_id))
        if not channel:
            return {
                "messages": [],
                "error": f"Channel with ID {channel_id} not found"
            }

        # Parse timestamp
        since = datetime.fromisoformat(since_timestamp.replace("Z", "+00:00"))

        # Fetch messages (discord.py's list_messages is for pagination, not time range)
        # We'll use history() with limit to get recent messages
        messages = []
        async for msg in channel.history(after=since, limit=10000):
            messages.append({
                "id": str(msg.id),
                "author": str(msg.author),
                "content": msg.content or "",
                "timestamp": msg.created_at.isoformat(),
                "attachments": len(msg.attachments)
            })

        logger.info(f"Fetched {len(messages)} messages from channel {channel_id}")

        return {
            "messages": messages,
            "error": None
        }

    except ValueError as e:
        return {
            "messages": [],
            "error": f"Invalid timestamp format: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        return {
            "messages": [],
            "error": f"Failed to fetch messages: {str(e)}"
        }
