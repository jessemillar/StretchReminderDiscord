import discord
from discord.ext import commands, tasks

import os
import json
import time
import logging

logger = logging.getLogger(__name__)

class Reminder:
    def __init__(self, member):
        self.member = member
        logger.info("init self.member --> {0}".format(self.member))
        logger.info("init self.member.roles --> {0}".format(self.member.roles))
        self.timer_start = time.time()
        logger.info("Reminder created for {}".format(member.id))

    def reminder_time(self):
        logger.info("reminter_time self.member --> {0}".format(self.member))
        logger.info("reminter_time self.member.roles --> {0}".format(self.member.roles))
        reminder_role = discord.utils.find(lambda r: "hour" in r.name, self.member.roles)
        #  logger.info(reminder_role)
        logger.info("reminter_time reminder_role ---> {0}".format(reminder_role))
        return self.timer_start + float(reminder_role.name.split()[0]) * 3600

class AssignableRole(commands.RoleConverter):
    async def convert(self, ctx, argument):
        role = await super().convert(ctx, argument)
        if role.id in ctx.cog.config["assignable_role_ids"]:
            return role
        else:
            logger.info('Role "{}" is not assignable.'.format(argument))
            raise commands.BadArgument('Role "{}" is not assignable.'.format(argument))

class AutoReminders(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.reminders = []

        # Start task
        self.remind.start()

    def cog_unload(self):
        self.remind.cancel()

    def cog_check(self, ctx):
        # Only cog only usable within osu! Stretch reminders guild
        logger.info(ctx.guild.id)
        logger.info(self.bot.config)
        logger.info(ctx.guild.id == self.bot.config["guild_id"])
        return ctx.guild.id == self.bot.config["guild_id"]

    def add_reminder(self, member):
        logger.info("member --> {0}".format(member.roles))
        if next((r for r in self.reminders if r.member == member), None) is not None:
            return
        # osu reminder members if they are playing osu
        if member.activity != None and member.activity.name in self.config["osu_game_names"] and discord.utils.find(lambda r: r.name.endswith(" hour"), member.roles):
            self.reminders.append(Reminder(member))
        # any game reminder members if they are playing a game
        elif member.activity != None and discord.utils.find(lambda r: r.name.endswith(" any"), member.roles):
            self.reminders.append(Reminder(member))
        # always reminder members if they are online
        elif member.status != discord.Status.offline and discord.utils.find(lambda r: r.name.endswith(" online"), member.roles):
            self.reminders.append(Reminder(member))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.reminders = [r for r in self.reminders if r.member != member]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # check if member has a reminder role
        reminder_role = discord.utils.find(lambda r: "hour" in r.name, after.roles)
        if not reminder_role:
            return

        # if member only wants to be notified while playing osu
        if reminder_role.name.endswith("hour"):
            # if user wasnt playing osu, and now is
            if (before.activity == None or before.activity.name not in self.config["osu_game_names"]) and (after.activity != None and after.activity.name in self.config["osu_game_names"]):
                # set reminder
                self.reminders.append(Reminder(after))
                logger.info("Set reminder for {}".format(after.id))
            # elif user was playing osu, and now isnt
            elif (before.activity != None and before.activity.name in self.config["osu_game_names"]) and (after.activity == None or after.activity.name not in self.config["osu_game_names"]):
                # cancel reminder
                self.reminders = [r for r in self.reminders if r.member != after]
                logger.info("Cancelled reminder for {}".format(after.id))
        # if member wants to be notified when playing any game
        elif reminder_role.name.endswith("any"):
            # if user wasnt playing a game
            if before.activity == None and after.activity != None:
                # set reminder
                self.reminders.append(Reminder(after))
                logger.info("Set reminder for {}".format(after.id))
            # elif user was playing a game, and now isnt
            elif before.activity != None and after.activity == None:
                # cancel reminder
                self.reminders = [r for r in self.reminders if r.member != after]
                logger.info("Cancelled reminder for {}".format(after.id))
        # if member wants to be notified when online
        elif reminder_role.name.endswith("online"):
            # if user wasnt online and now is
            if before.status == discord.Status.offline and after.status != discord.Status.offline:
                # set reminder
                self.reminders.append(Reminder(after))
                logger.info("Set reminder for {}".format(after.id))
            # elif user was online and now isnt
            elif before.status != discord.Status.offline and after.status == discord.Status.offline:
                # cancel reminder
                self.reminders = [r for r in self.reminders if r.member != after]
                logger.info("Cancelled reminder for {}".format(after.id))

    @commands.command(name="set")
    @commands.guild_only()
    async def setrole(self, ctx, *, role: AssignableRole):
        logger.info("Cancelling reminder for {}".format(ctx.author.id))
        # Remove current reminder role
        await ctx.author.remove_roles(*[r for r in ctx.author.roles if r.id in self.config["assignable_role_ids"]], reason="Setting new exclusive role")

        # Add new role
        await ctx.author.add_roles(role, reason="Role requests via command")
        await ctx.send('"{0.name}" has been set for {1.mention}.'.format(role, ctx.author))

        # Remove old reminder and add new reminder
        self.reminders = [r for r in self.reminders if r.member != ctx.author]
        logger.info("Cancelled reminder for {}".format(ctx.author.id))
        self.add_reminder(ctx.author)

    @setrole.error
    async def setrole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        # Remove reminder
        self.reminders = [r for r in self.reminders if r.member != ctx.author]
        logger.info("Cancelled reminder for {}".format(ctx.author.id))

        # Remove current reminder role
        await ctx.author.remove_roles(*[r for r in ctx.author.roles if r.id in self.config["assignable_role_ids"]], reason="Setting new exclusive role")
        await ctx.send('Reminders have been stopped for {0.mention}.'.format(ctx.author))

    @setrole.error
    async def setrole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)

    @tasks.loop(seconds=5.0)
    async def remind(self):
        for reminder in self.reminders:
            logging.info(reminder)
            if reminder.reminder_time() < time.time():
                logger.info("Reminder sending for {reminder.member.id}")
                reminder_channel = self.bot.get_channel(self.config["reminder_channel_id"])
                await reminder_channel.send("It's stretching time, {0.mention}!".format(reminder.member))
                logger.info(f"Reminder sent for {reminder.member.id}")
                reminder.timer_start = time.time()

    @remind.before_loop
    async def before_remind(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.bot.config["guild_id"])
        for member in guild.members:
            self.add_reminder(member)

def setup(bot):
    abs_path = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(abs_path, "autoreminders.config.json")
    with open(config_path) as fp:
        config = json.load(fp)
        bot.add_cog(AutoReminders(bot, config))
