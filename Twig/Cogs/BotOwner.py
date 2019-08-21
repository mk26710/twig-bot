# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from discord.ext import commands
from Twig.TwigCore import *


# ====================================


class BotOwner(commands.Cog, name='Гадости'):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    # COMMANDS
    @commands.command(name='role_color', brief='Изменяет цвет роли')
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def _role_color(self, ctx, r: discord.Role, c: discord.Color = None):
        if c is None:
            current_color = r.colour

            return await ctx.send(embed=discord.Embed(
                title=f'Цвет {r.name} ({r.id})',
                description=f'HEX: `{str(current_color)}`',
                colour=current_color
            ))

        await r.edit(colour=c)

        r_color_embed = discord.Embed(
            colour=c, description=f"Вы успешно изменили цвет для роли **{r}**!",
            reason=f"Изменено пользователем {ctx.author.id}")
        r_color_embed.set_footer(
            text=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})",
            icon_url=ctx.author.avatar_url)

        await ctx.send(embed=r_color_embed)

    @commands.command()
    async def check_existence(self, ctx, user: discord.User):
        if user is self.bot.user:
            return await ctx.send(f"Оу. Но создатель решил, что я не могу иметь уровень! Просите. Бип. Буп.")

        a = await fetch_data('user', 'user', user.id)
        if a is None:
            await ctx.send(':x: %s (`%s`) нет в базе данных' % (user, user.id))
        else:
            await ctx.send(':white_check_mark: %s (`%s`) присутствует в базе данных' % (user, user.id))

    @commands.command(aliases=['update'])
    async def pull(self, ctx):
        try:
            message = await ctx.send(':repeat: Pulling from origin master...')
            repo = git.Repo('.git')
            assert not repo.bare
            repository = repo.remotes.origin
            repository.fetch()
            repository.pull()
            await message.edit(content='**✓** `origin` fetched & pulled successfully! \n' +
                                       '**!!!** Hot Reload is required. Hard reset is recommended.')
            del repo, message, repository
        except Exception as err:
            await message.edit(content='Ошибка! ' + '```' + str(err) + '```')
            raise err

    @commands.command()
    async def fetch_users(self, ctx):
        message = await ctx.send(':repeat: Вам придётся немного подождать...')

        data = await fetch_whole_table()
        resulting_txt = "Список пользователей в БД: ```yaml\n"

        approx_fetch_time = len(data) * 2
        approx_fetch_time = round((approx_fetch_time / 60), 2)

        await message.edit(content=":repeat: Вам придётся немного подождать...\n" +
                                   f":hourglass: Процесс может занять **{approx_fetch_time}** мин.")

        if len(data) >= 35:
            resulting_txt = f"Список пользователей слишком длинный. \nВсего строк в таблице: **{len(data)}**"
            return await message.edit(content=resulting_txt)

        for i in range(0, len(data)):
            user = await self.bot.fetch_user(int(data[i]))
            await asyncio.sleep(2)
            # print(f'[FETCH] Processing user {user.name}#{user.discriminator} ({user.id})')
            resulting_txt = resulting_txt + str(user) + ' (' + str(user.id) + ')' + "\n"

        resulting_txt = f'Всего записей: **{len(data)}**\n' + resulting_txt + '```'

        if len(resulting_txt) >= 1800:
            resulting_txt = f"Список пользователей слишком длинный. \nВсего строк в таблице: **{len(data)}**"
            return await message.edit(content=resulting_txt)

        await asyncio.sleep(0.05)
        return await message.edit(content=resulting_txt)

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    # ==== GUILD COMMANDS ==== #

    @commands.group(name='guild', brief='Манипуляции с серверами, где я есть')
    async def _guild(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали субкоманду (`leave`, `list`)')

    @_guild.command(name='list')
    async def _guild_list(self, ctx):
        guilds_ls = self.bot.guilds

        resulting_txt = "```xl\n"

        for i in range(len(guilds_ls)):
            resulting_txt = resulting_txt + "\n" + str(guilds_ls[i]) + " (" + str(guilds_ls[i].id) + ")"

        resulting_txt += "```"
        del guilds_ls
        return await ctx.send(resulting_txt)

    @_guild.command(name='leave')
    async def _guild_leave(self, ctx, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            await guild.leave()
            await ctx.send(f"Я успешно покинул сервер {guild.name} ({guild.id})")
        except Exception as err:
            log_chan = self.bot.get_channel(BOT_MAIN_LOGS)
            return await log_chan.send(
                f"Бип. Буп. Что-то пошло не так. Передайте это моему создателю: "
                + "```" + str(err) + "```"
            )

    @commands.group()
    async def shutdown(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Укажите флаг команды.' +
                           '\n**Использование**: `%sshutdown [-r | -fs]`' % BOT_PREFIX)

    # ==== SHUTDOWN COMMANDS ==== #

    @shutdown.command(aliases=['-r'])
    async def r(self, ctx):
        LOG_CHANNEL = self.bot.get_channel(BOT_MAIN_LOGS)
        import datetime
        await ctx.send(":gear: Перезагрузка...")
        await LOG_CHANNEL.send(embed=discord.Embed(
            colour=0x9B59B6,
            title='Перезагрузка',
            description='**%s** (`%s`) перезагружает бота...'
                        % (str(ctx.author), str(ctx.author.id)),
            timestamp=datetime.datetime.now()
        ))
        await self.bot.close()
        quit()

    @shutdown.command(aliases=['-fs'], enabled=False)
    async def fs(self, ctx):
        LOG_CHANNEL = self.bot.get_channel(BOT_MAIN_LOGS)
        import datetime
        await ctx.send(":gear: Завершение работы...")
        await LOG_CHANNEL.send(embed=discord.Embed(
            colour=0xF55E5E,
            title='Завершение работы',
            description='**%s** (`%s`) выключает бота...'
                        % (str(ctx.author), str(ctx.author.id)),
            timestamp=datetime.datetime.now()
        ))
        await self.bot.close()
        os.system("service twig stop")
        quit()

    # ==== STATUS COMMANDS ==== #

    @commands.group(name='status')
    async def _status(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Вы не указали субкоманду, либо вы указали неверную субкоманду.")

    @_status.command(name='reset')
    async def _status_reset(self, ctx):
        playing_now = discord.Activity(name=BOT_PLAYING_GAME_NAME + f' | {BOT_PREFIX}help',
                                       type=discord.ActivityType.playing)
        await self.bot.change_presence(activity=playing_now)

        return await ctx.send(f'Статус успешно восстановлен!')

    @_status.command(name='set')
    async def _status_set(self, ctx, status_type, *, text):
        if (status_type == 'playing') or (status_type == '1'):
            status_type = discord.ActivityType.playing
        elif (status_type == 'watching') or (status_type == '2'):
            status_type = discord.ActivityType.watching
        elif (status_type == 'listening') or (status_type == '3'):
            status_type = discord.ActivityType.listening
        # Немного сломано, нужно понять в чём проблема.
        elif (status_type == 'streaming') or (status_type == '4'):
            status_type = discord.ActivityType.streaming
        # Если в качестве типа статуса было указано что-то странное
        else:
            status_type = discord.ActivityType.playing

        playing_now = discord.Activity(name=str(text),
                                       type=status_type)
        await self.bot.change_presence(activity=playing_now)

        return await ctx.send(f'Статус успешно восстановлен!')


def setup(client):
    client.add_cog(BotOwner(client))
