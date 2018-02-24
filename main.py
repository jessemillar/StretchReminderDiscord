import asyncio
import logging
import discord
import collections
import time

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

client = discord.Client()

class Reminder:
    def __init__(self, member, timer_start=None):
        self.member = member
        self.timer_start = timer_start or time.time()
        logging.info("Reminder created: " + str(self))
    
    def reminder_time(self):
        reminder_role = discord.utils.find(lambda r: r.name.endswith(" hour"), self.member.roles)
        return self.timer_start + float(reminder_role.name.split()[0]) * 3600

    def __repr__(self):
        return "{} {}".format(self.member.name, self.reminder_time())

reminders = []

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

    # On startup, check for users who are playing osu! and set their reminders
    global reminders
    for member in client.get_server("412943020850413570").members:
        if member.game != None and member.game.name == "osu!" and discord.utils.find(lambda r: r.name.endswith(" hour"), member.roles):
            reminders.append(Reminder(member))
        # would use >"any" in ...< but not sure how roles are formatted
        elif member.game != None and discord.utils.find(lambda r: r.name.endswith(" any"), member.roles):
            reminders.append(Reminder(member))

@client.event
async def on_message(message):
    # check for !set command
    if message.content.lower().startswith("!set ") and len(message.content.split()) > 1:
        await update_role(message)

@client.event
async def on_member_update(before, after):
    # check if member has a reminder role
    reminder_role = discord.utils.find(lambda r: "hour" in r.name, after.roles)
    if not reminder_role:
        return

    global reminders
    # if member only wants to be notified while playing osu
    if "any" not in reminder_role:
        # if user wasnt playing osu, and now is
        if (before.game == None or before.game.name != "osu!") and (after.game != None and after.game.name == "osu!"):
            # set reminder
            reminders.append(Reminder(after))
            logging.info("Set reminder for {} ({})".format(after.name, after.id))
        # elif user was playing osu, and now isnt
        elif (before.game != None and before.game.name == "osu!") and (after.game == None or after.game.name != "osu!"):
            # cancel reminder
            reminders = [r for r in reminders if r.member != after]
            logging.info("Cancelled reminder for {} ({})".format(after.name, after.id))
    else:
        # if user wasnt playing a game
        if before.game == None and after.game != None:
            # set reminder
            reminders.append(Reminder(after))
            logging.info("Set reminder for {} ({})".format(after.name, after.id))
        # elif user was playing a game, and now isnt
        elif before.game != None and after.game == None:
            # cancel reminder
            reminders = [r for r in reminders if r.member != after]
            logging.info("Cancelled reminder for {} ({})".format(after.name, after.id))

async def update_role(message):
    role_name = message.content.split(maxsplit=1)[1].lower()
    hour_options = ["0.5", "1", "2", "3"]
    role_options = []
    for hour in hour_options:
        role_options.append(hour + " hour")
        role_options.append(hour + " hour any")
    if role_name == "none":
        await client.remove_roles(message.author, *[r for r in message.author.roles if r.name.endswith(" hour")])
        await client.send_message(message.channel, "Reminders stopped for {}".format(message.author.mention))
        logging.info("Removing roles from {} ({})".format(message.author.name, message.author.id))
    elif role_name in role_options:
        role = discord.utils.get(message.server.roles, name=role_name)
        await client.replace_roles(message.author, *([r for r in message.author.roles if not r.name.endswith(" hour")] + [role]))
        await client.send_message(message.channel, "{} reminders set for {}".format(role_name, message.author.mention))
        logging.info("Setting {} role from {} ({})".format(role_name, message.author.name, message.author.id))
    else:
        await client.send_message(message.channel, "{} is not a valid role {}".format(role_name, message.author.mention))

async def reminder_checks():
    global reminders
    await client.wait_until_ready()
    reminder_channel = discord.Object(id="412943327688785920")  # channel: #reminders
    passed_reminders = []
    
    while not client.is_closed:
        for reminder in reminders:
            if reminder.reminder_time() < time.time():
                passed_reminders.append(reminder)
        
        if len(passed_reminders) > 0:
            for reminder in passed_reminders:
                reminders = [r for r in reminders if r.member.id != reminder.member.id] # remove old reminder
                reminders.append(Reminder(reminder.member)) # create new reminder
            mentions = " ".join([ reminder.member.mention for r in passed_reminders ])
            await client.send_message(reminder_channel, mentions + " Time to stretch!")
            logging.info("Reminder sent to: " + ", ".join([ r.member.name for r in passed_reminders ]))

        passed_reminders.clear()
        await asyncio.sleep(10)


def main():
    with open("token") as fp:
        token = fp.read()

    client.loop.create_task(reminder_checks())
    client.run(token)

if __name__ == '__main__':
    main()

