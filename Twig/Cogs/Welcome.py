from discord.ext import commands
import discord
from Twig.TwigCore import *
from Twig.Utils.Logger import Logger


class Welcomer(commands.Cog, name="Добро пожаловать"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        try:
            default_channel = discord.utils.get(member.guild.channels, name="general")

            message = await default_channel.send(embed=discord.Embed(
                colour=0xFFFFFF,
                description=f'Хэй, **{member.name}**! Добро пожаловать к нам!'
            ).set_author(
                name=f'{member.name}#{member.discriminator}'
            ).set_footer(
                text=f'Участник #{member.guild.member_count}'
            ).set_thumbnail(
                url=member.avatar_url)
            )

            return await message.delete(delay=30)

        except Exception as err:
            await Logger(
                logger_type='err', logger_title=':x: Ошибка',
                logger_info=f'{str(err)}',
                log_to=BOT_MAIN_LOGS, client=self.bot
            ).send_log()
            raise err


def setup(bot):
    bot.add_cog(Welcomer(bot))
