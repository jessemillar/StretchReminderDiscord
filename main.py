import discord

import json
import logging

from bot import StretchRemindersBot

def main():
    # Setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("stretchremindersbot.log")
    file_handler.setLevel(logging.ERROR)
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("{asctime}:{levelname}:{name}: {message}", datefmt=datefmt, style="{")
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Load config json
    with open("config.json") as fp:
        config = json.load(fp)

    # Initialise bot instance
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    bot = StretchRemindersBot(command_prefix="!", intents=intents)

    # Load extensions
    bot.load_extension("cogs.admin")
    bot.load_extension("cogs.autoreminders")

    # Start bot loop
    bot.run(config)

if __name__ == "__main__":
    main()
