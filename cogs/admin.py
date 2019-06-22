from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx, extension_name):
        try:
            self.bot.reload_extension(extension_name)
            await ctx.send("`{0}` successfully reloaded.".format(extension_name))
        except commands.ExtensionError as e:
            await ctx.send(e)

def setup(bot):
    bot.add_cog(Admin(bot))
