"""Ollama client with function calling support and context management."""

import discord
import requests
import asyncio
import json
from typing import List, Dict, Any, Optional
from src.summarize_bot.discord_tool import get_messages
from src.summarize_bot.prompt import ANALYSIS_PROMPT
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, url: str, model: str, max_context_tokens: int, bot: discord.Client = None):
        """
        Initialize Ollama client.

        Args:
            url: Ollama server URL (e.g., http://localhost:11434)
            model: Model name to use (e.g., llama3)
            max_context_tokens: Maximum context window size
            bot: Optional Discord client instance for tool access
        """
        self.url = url.rstrip("/")
        self.model = model
        self.max_context_tokens = max_context_tokens
        self.bot = bot

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (simplified approximation)."""
        # Rough approximation: ~4 characters per token
        return len(text) // 4

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool function.

        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments for the tool

        Returns:
            Tool result
        """
        if tool_name == "get_messages":
            return await get_messages(self.bot, tool_args["channel_id"], tool_args["since_timestamp"])
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def summarize_analyze(self, messages: List[Dict[str, Any]]) -> str:
        """
        Generate a summary analyzing provided messages directly (no tool calling).

        Args:
            messages: List of message dictionaries from get_messages tool

        Returns:
            Summary string
        """
        # Build conversation messages
        # Add analysis prompt as system message
        messages_with_prompt = [
            {"role": "system", "content": ANALYSIS_PROMPT},
        ]

        # Add each message to the conversation
        # Messages from get_messages have id, author, content, timestamp, attachments - no role field
        for msg in messages:
            # Filter out messages from the bot itself
            author_name = msg.get('author', '')
            if author_name == self.bot.bot_name:
                logger.debug(f"Skipping bot message from: {author_name}")
                continue

            # Format the message for the LLM
            content_text = f"Author: {author_name}\n"
            content_text += f"Time: {msg.get('timestamp', 'Unknown')}\n"
            content_text += f"Content: {msg.get('content', '')}\n"
            if msg.get('attachments', 0) > 0:
                content_text += f"Attachments: {msg.get('attachments', 0)}\n"

            messages_with_prompt.append({
                "role": "user",
                "content": content_text
            })

        logger.info(f"Sending {len(messages)} messages to LLM for analysis")

        # Make request to Ollama
        response = self._ollama_request_analyze(messages_with_prompt)

        if "error" in response:
            raise Exception(f"Ollama API error: {response['error']}")

        logger.info(f"LLM Response: {json.dumps(response, indent=2, default=str)}")

        content = response.get("message", {}).get("content", "")
        # Check if LLM provided a final response (not a function call)
        if not content or not content.strip().startswith("[Function call]"):
            logger.info("LLM provided final response")
            return content
        else:
            raise Exception("Unexpected response format from LLM")

    def _ollama_request_analyze(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make request to Ollama API for analysis (no tools)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.url}/api/chat",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise Exception(f"Failed to communicate with Ollama: {str(e)}")

    def _ollama_request(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make request to Ollama API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(
                f"{self.url}/api/chat",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise Exception(f"Failed to communicate with Ollama: {str(e)}")
