from discord.ext import commands
from Twig.TwigCore import *


class CommandErrorHandler(commands.Cog, name='Обработка ошибок'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Это событие вызывается, когда случаются ошибки во время использования команд.
        ctx   : Context
        error : Exception"""

        # Это предотвращает обработку ошибок для команд, с локальным обработчиками
        if hasattr(ctx.command, 'on_error'):
            return

        # ignored = commands.UserInputError
        log_channel = self.bot.get_channel(BOT_MAIN_LOGS)
        error = getattr(error, 'original', error)

        # Все типы ошибок, внутри ignored - будут игнорироваться обработчиком
        # if isinstance(error, ignored):
        #    return

        # ==== DISCORD PYTHON ERRORS ====

        if isinstance(error, commands.CommandNotFound):
            return await ctx.send('Что это вообще за команда? Я такую не знаю :(')

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'Команда `{ctx.command}` отключена.')

        elif isinstance(error, commands.MissingPermissions):
            if is_no_perm_notifications_enabled is True:
                return await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        elif isinstance(error, commands.CheckFailure):
            if is_no_perm_notifications_enabled is True:
                return await ctx.send(f':lock: У вас нет доступа к команде `{ctx.command}`')
            else:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(
                title=':warning: Операция прервана!',
                description='Вы пропустили какой-то важный параметр для команды!',
                colour=WARNING_COLOR
            ).set_footer(
                text='Узнать подробнее о команде: %shelp %s' % (BOT_PREFIX, ctx.command)
            ))

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    embed=discord.Embed(title=':x: Ошибка!', colour=ERROR_COLOR,
                                        description=f'Команду `{ctx.command}` нельзя использовать в ЛС'))
                return await log_channel.send(
                    embed=discord.Embed(
                        title=':x: Ошибка!', colour=ERROR_COLOR, description=f'{str(error)}').add_field(
                        name='Пытался использовать в ЛС', value=str(ctx.author) + ' (' + str(ctx.author.id) + ')')
                )
            except:
                pass

        # Обрвботчики для конкретных случаев
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'userinfo':
                return await ctx.send(embed=discord.Embed(
                    title=':x: Произошла ошибка!',
                    colour=ERROR_COLOR,
                    description='Пользователь не найден.'
                ))

            elif ctx.command.qualified_name == 'axp add_user':  # Проверяет, если команда 'axp add_user'
                return await ctx.send(embed=discord.Embed(
                    title=':x: Операция прервана.',
                    colour=ERROR_COLOR,
                    description='Я ни разу не встречал этого пользователя, поэтому я не могу добавить его в БД.'
                ))

            elif ctx.command.qualified_name == 'xp':
                return await ctx.send(embed=discord.Embed(
                    title=':x: Произошла ошибка!',
                    colour=ERROR_COLOR,
                    description='Я не знаю такого пользователя.'
                ))

            elif ctx.command.qualified_name == 'role_color':
                return await ctx.send(embed=discord.Embed(
                    title=':x: Произошла ошибка!',
                    colour=ERROR_COLOR,
                    description='Неизвестная роль.'
                ))

        elif isinstance(error, discord.errors.NotFound):
            if ctx.command.qualified_name == 'voicedemo':
                return await ctx.send(embed=
                discord.Embed(
                    title=':x: Ошибка!',
                    description='Канал не найден.',
                    colour=ERROR_COLOR
                )
                )

        # Ошибки для конкретных команд по кодам ошибки (404, 403 и т.п.)
        elif isinstance(error, discord.errors.HTTPException):
            if ctx.command.qualified_name == 'voicedemo':
                if error.code == 50035:
                    return await ctx.send(embed=
                    discord.Embed(
                        title=':x: Ошибка!',
                        description='Канал не найден.',
                        colour=ERROR_COLOR
                    ).add_field(
                        name='Дополнительно',
                        value='ID канала не может быть больше значения **%s**' % re.findall(r'\d+', error.text)[0]
                    )
                    )

            elif ctx.command.qualified_name == 'role_color':
                if error.code == 50013:
                    return await ctx.send(embed=
                    discord.Embed(
                        title=':x: Ошибка!',
                        description='Недостаточно прав.',
                        colour=ERROR_COLOR
                    )
                    )

        # ==== COOLDOWN CHECKS ====

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.message.author.id in BOT_MAINTAINERS or await ctx.bot.is_owner(ctx.message.author):
                await ctx.reinvoke()
                return
            return await ctx.send(
                f'Вы не можете использовать эту команду ещё **{round(error.retry_after, 2)}** секунд.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    """Пример локального обработчика событий для команды do_repeat"""

    @commands.command(name='repeat', aliases=['mimic', 'copy'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def do_repeat(self, ctx, *, inp: str):
        await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("А что повторять-то?")


def setup(client):
    client.add_cog(CommandErrorHandler(client))
