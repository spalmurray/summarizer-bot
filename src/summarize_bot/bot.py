"""Discord bot implementation."""

import discord
from discord import app_commands
import discord.utils
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.summarize_bot.ollama_client import OllamaClient
from src.summarize_bot.commands import setup_commands
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# For sync commands to a specific guild
MY_GUILD = discord.Object(id=int(os.getenv("DISCORD_GUILD_ID", "0")))  # Replace with your guild ID


class SummarizeBot(discord.Client):
    """Discord bot for message summarization."""

    def __init__(self):
        """Initialize bot with intents."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.dm_messages = True
        intents.reactions = True

        super().__init__(intents=intents)

        # Store bot username for filtering messages
        self.bot_name = None

        # Initialize Ollama client (pass self for tool access)
        self.ollama_client = OllamaClient(
            url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
            bot=self
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """Set up bot after being connected."""
        # Register commands
        setup_commands(self.tree, self.ollama_client)

        # Sync commands to Discord
        try:
            if MY_GUILD.id > 0:
                # Sync to specific guild (faster, doesn't need propagation)
                logger.info(f"Found {len(self.tree.get_commands())} command(s) in tree")
                synced = await self.tree.sync(guild=MY_GUILD)
                logger.info(f"Synced {len(synced)} command(s) to guild {MY_GUILD.id}")
                for cmd in synced:
                    logger.info(f"  - {cmd.name}")
            else:
                # Sync globally (can take up to an hour to propagate)
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s) globally to Discord")
                for cmd in synced:
                    logger.info(f"  - {cmd.name}")
        except Exception as e:
            logger.error(f"Failed to sync commands: {str(e)}")

        logger.info("Bot setup complete")

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        # Store bot username for filtering
        self.bot_name = str(self.user)


def main():
    """Run the bot."""
    # Get Discord token from environment
    discord_token = os.getenv("DISCORD_TOKEN")

    if not discord_token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        logger.error("Please set it in your .env file")
        return

    # Create and run bot
    bot = SummarizeBot()

    try:
        bot.run(discord_token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token. Please check your DISCORD_TOKEN.")
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
