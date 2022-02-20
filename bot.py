import discord
from discord.ext import commands

import sys
import logging
import traceback

logger = logging.getLogger(__name__)

class StretchRemindersBot(commands.Bot):
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f"{original.__class__.__name__}: {original}", file=sys.stderr)

    async def on_ready(self):
        logger.info("Bot ready...")

    def run(self, config):
        logger.info("Bot starting...")
        self.config = config
        super().run(config["bot_token"])
