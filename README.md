# StretchReminderDiscord
Bot that manages the osu! Stretch reminders discord server.
As currently is, the bot is simply made to work, not be pretty.
Will likely rewrite with a proper structure at a later date.

## Setup

- pip3 install -r requirements.txt
- python3 -m pip install -U discord.py
- python3 main.py

- Enable the members and presences intents on your Discord bot page

## TODO
- Set custom presence in bot.py occasionally
- Document setting up the bot in the developer portal
- Document config.json
	{
	"bot_token": "token123"
	"guild_id": 1234
	}
- Document cogs/autoreminders.config.json ("guild_id" is your server ID)
	{
	"osu_game_names": [""],
	"assignable_role_ids": [5678],
	"reminder_channel_id": 1234
	}

## Instructions
(Taken from the Osu discord: https://discord.gg/zPBHeex https://www.reddit.com/r/osugame/comments/7xh41z/stretching_reminder_discord/)

-----------------------------------------

INSTRUCTIONS

1. Set discord to display your current game (check the Games section in discord settings)
2. Assign yourself a reminder role with the !set command in chat

-----------------------------------------

REMINDER ROLES

0.5 hour reminds you each half hour
1 hour reminds you each hour (recommended)
2 hour reminds you each 2 hours
3 hour reminds you each 3 hours
Each of the above roles can also be enabled for non-osu! games or simply being online by adding any or online to the end respectivly

Examples:
!set 1 hour
!set 2 hour
!set 1 hour any
!set 0.5 hour any
!set 1 hour online

-----------------------------------------

INFO

Reminders are only sent if you are currently playing osu! so you dont have to worry about being spammed with mentions
Reminders are sent as mentions in reminders
GIF versions of stretches are found in stretches
Dr Levi recommands taking a 5 minute break each hour to focus on stretches, but its also a good idea to get up, drink some water, and take a short walk each few hours
To stop reminders, issue the command !stop
If reminders aren't working for you, try setting your discord status to invisible and back
If reminders aren't working for anyone, the bot died and needs to be restarted (mention @Syrin)

-----------------------------------------

