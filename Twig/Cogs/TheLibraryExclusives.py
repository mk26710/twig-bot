from discord.ext import commands
from Twig.TwigCore import *


class TheLibraryExclusives(commands.Cog, name="Дополнительно"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fact", hidden=True)
    async def _test_test_(self, ctx):
        return await ctx.send('Facts.')


def setup(bot):
    bot.add_cog(TheLibraryExclusives(bot))
