import asyncio
import logging
import discord
import collections
import time

logger = logging.getLogger("discord")
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

client = discord.Client()

class Reminder:
    def __init__(self, user, remind_time):
        self.user = user
        self.remind_time = remind_time
    
    def __repr__(self):
        return "{} {}".format(self.user.name, self.remind_time)

reminders = []

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

@client.event
async def on_member_update(before, after):
    global reminders
    # if user wasnt playing osu, and now is
    if (before.game == None or before.game.name != "osu!") and (after.game != None and after.game.name == "osu!"):
        # set reminder
        reminders.append(Reminder(after, time.time() + 3600))
        logging.info("Set reminder for {} ({})".format(after.name, after.id))
    # elif user was playing osu, and now isnt
    elif (before.game != None and before.game.name == "osu!") and (after.game == None or after.game.name != "osu!"):
        # cancel reminder
        reminders = [r for r in reminders if r.user != after]
        logging.info("Cancelled reminder for {} ({})".format(after.name, after.id))

async def reminder_checks():
    await client.wait_until_ready()
    reminder_channel = discord.Object(id="412943327688785920")  # channel: #reminders
    passed_reminders = []
    
    while not client.is_closed:
        for reminder in reminders:
            if reminder.remind_time < time.time():
                passed_reminders.append(reminder)
                reminder.remind_time += 3600
        
        if len(passed_reminders) > 0:
            mentions = " ".join([ reminder.user.mention for r in passed_reminders ])
            await client.send_message(reminder_channel, mentions + " Time to stretch!")
            logging.info("Reminder sent to: " + ", ".join([ r.user.name for r in passed_reminders ]))

        passed_reminders.clear()
        await asyncio.sleep(10)


def main():
    with open("token") as fp:
        token = fp.read()

    client.loop.create_task(reminder_checks())
    client.run(token)

if __name__ == '__main__':
    main()

