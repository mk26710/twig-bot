from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.Logger import Logger
from Twig.Utils.UserConverter import Target


# ====================================

class Admin(commands.Cog, name='Админские'):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in BOT_MAINTAINERS

    @commands.command(name='what_shard', aliases=['get_shard', 'find_shard', 'find_me', 'findme'], brief='Необходимо для выявления проблем', hidden=True)
    @commands.cooldown(1, 60, type=BucketType.member)
    async def _what_shard(self, ctx):
        guild = ctx.guild
        guilds_shard = guild.shard_id
        return await ctx.send(embed=discord.Embed(
            colour=0xFFFFFF,
            description=f':office: Идентификатор данного сервера: **#`{guild.id}`**\n'
                        f':diamond_shape_with_a_dot_inside: Номер кластера для данного сервера: **#`{guilds_shard}`**'
        ).set_author(
            name=guild.name, icon_url=guild.icon_url
        ))

    # ===== XP MANAGEMENT AREA ======

    @commands.group()
    async def axp(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send("Вы не указали субкоманду, либо вы указали неверную субкоманду.")

    @axp.command()
    async def add(self, ctx, user: discord.User, xp):
        user = Target(user)

        if user.original is self.bot.user:
            return await ctx.send("Оу. Но создатель решил, что я не могу иметь уровень! Простите. Бип. Буп.")

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя сюда.')

        a = await fetch_data('user', 'user', user.intID)
        if a is None:
            del a
            return await ctx.send(
                embed=discord.Embed(
                    colour=ERROR_COLOR,
                    title=':x: Операция отменена',
                    description=f'**{user.tag}** (`{user.strID}`) отсутствует в базе данных.'
                )
            )

        triggered_at = time.time()
        message = await ctx.send(embed=discord.Embed(
            title=':repeat: Операция выполняется...',
            description='Пожалуйста, ждите!',
            colour=SECONDARY_COLOR
        ))

        prev_xp = int(await fetch_data('xp', 'user', user.strID))
        temp_xp = prev_xp + int(xp)
        await update_data('xp', temp_xp, 'user', user.strID)
        done_at = time.time()
        done_after = done_at - triggered_at
        done_after = str(round(done_after * 1000, 2))
        del done_at, triggered_at

        await Logger(
            logger_type='info', logger_title='Админское изменение баланса',
            logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                        f' изменяет баланс **{user.tag}** (`{user.strID}`)\n\n' +
                        f'**Добавляет к балансу:** {xp} очков опыта\n' +
                        f'**Новый баланс:** {temp_xp} очков опыта',
            log_to=BOT_XP_LOGS, client=self.bot
        ).send_log()

        return await message.edit(
            embed=discord.Embed(
                title=':white_check_mark: Операция выполнена!',
                description=f"К балансу {user.tag} (`{user.strID}`) добавлено **{xp}** очков опыта",
                colour=SUCCESS_COLOR
            ).set_footer(
                text=f'Запрошено пользователем {ctx.author.name}' + f' | Выполнено за {done_after} мс'
            )
        )

    @axp.command()
    async def set(self, ctx, user: discord.User, xp):
        user = Target(user)

        if user.original is self.bot.user:
            return await ctx.send("Оу. Но создатель решил, что я не могу иметь уровень! Простите. Бип. Буп.")

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя сюда.')

        a = await fetch_data('user', 'user', user.intID)
        if a is None:
            del a
            return await ctx.send(
                embed=discord.Embed(
                    colour=ERROR_COLOR,
                    title=':x: Операция отменена',
                    description=f'**{user.tag}** (`{user.strID}`) отсутствует в базе данных.'
                )
            )

        message = await ctx.send(embed=discord.Embed(
            title=':repeat: Операция выполняется...',
            description='Пожалуйста, ждите!',
            colour=SECONDARY_COLOR
        ))

        await update_data('xp', xp, 'user', user.intID)

        new_xp = await fetch_data('xp', 'user', user.intID)

        await Logger(
            logger_type='info', logger_title='Админское изменение баланса',
            logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                        f' изменяет баланс **{user.tag}** (`{user.strID}`)\n\n' +
                        f'**Новый баланс:** {new_xp} очков опыта',
            log_to=BOT_XP_LOGS, client=self.bot
        ).send_log()

        return await message.edit(
            embed=discord.Embed(
                title=':white_check_mark: Операция выполнена!',
                description=f"Баланс **{user.tag}** (`{user.strID}`) изменён на **{new_xp} опыта**",
                colour=SUCCESS_COLOR
            ).set_footer(
                text=f'Запрошено пользователем {ctx.author.name}')
        )

    @axp.command()
    @commands.is_owner()
    async def add_user(self, ctx, user: discord.User):
        if user is self.bot.user:
            return await ctx.send(f"Оу. Но создатель решил, что я не могу иметь уровень! Просите. Бип. Буп.")

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя сюда.')

        a = await fetch_data('user', 'user', user.id)

        user_tag = str(user.name + '#' + user.discriminator)

        if a is None:
            await add_user_into_data(user.id)

            await Logger(
                logger_type='success', logger_title='Добавление пользователя в БД',
                logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                            f' добавляет **{user}** (`{user.id}`) в базу данных',
                log_to=BOT_XP_LOGS, client=self.bot
            ).send_log()

            return await ctx.send(embed=discord.Embed(
                colour=SUCCESS_COLOR,
                title='Операция выполнена!',
                description=f':inbox_tray: **{user_tag}** (`{user.id}`) успешно добавлен в БД.'))
        else:
            return await ctx.send(embed=discord.Embed(
                title=':x: Ошибка!',
                colour=ERROR_COLOR,
                description=f'**{user_tag}** (`{user.id}`) уже находится в базе данных!'))

    @axp.command()
    @commands.is_owner()
    async def del_user(self, ctx, user: discord.User):
        user = Target(user)
        a = await fetch_data('user', 'user', user.intID)

        if a is None:
            return await ctx.send(embed=discord.Embed(
                title=':x: Ошибка!',
                colour=ERROR_COLOR,
                description=f'**{user.tag}** (`{user.strID}`) не найден в базе данных.'))

        await del_user_form_data(user.intID)

        await Logger(
            logger_type='err', logger_title='Удаление пользователя из БД',
            logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                        f' удаляет **{user.tag}** (`{user.strID}`) из базы данных',
            log_to=BOT_XP_LOGS, client=self.bot
        ).send_log()

        return await ctx.send(embed=discord.Embed(
            title='Операция выполнена!',
            description=f':outbox_tray: **{user.tag}** (`{user.strID}`) успешно удалён из БД.',
            colour=SUCCESS_COLOR
        ))

    @axp.command()
    @commands.is_owner()
    async def force_del_user(self, ctx, user):
        a = await fetch_data('user', 'user', user)

        if a is None:
            return await ctx.send(embed=discord.Embed(
                title=':x: Ошибка!',
                colour=ERROR_COLOR,
                description=f'**{user}** не найден в базе данных.'
            ))

        await del_user_form_data(user)

        await Logger(
            logger_type='err', logger_title='Удаление пользователя из БД',
            logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                        f' принудительно удаляет **{user}** из базы данных',
            log_to=BOT_XP_LOGS, client=self.bot
        ).send_log()

        return await ctx.send(embed=discord.Embed(
            title='Операция выполнена!',
            description=f':outbox_tray: **{user}** успешно удалён из БД.',
            colour=0xF55E5E
        ))

    @axp.command()
    async def reset(self, ctx, user: discord.User):
        user = Target(user)

        a = await fetch_data('user', 'user', user.intID)
        if a is None:
            return await ctx.send(embed=discord.Embed(
                title=':x: Ошибка!',
                colour=ERROR_COLOR,
                description=f'**{user.tag}** (`{user.strID}`) не найден в базе данных. \n\n'
                            + 'Если вам требуется обнулить его статистику, ' +
                            'воспользуйтесь принудительным удалением этого пользователя из БД.'
            ))

        await update_data('xp', 0, 'user', user.intID)

        await Logger(
            logger_type='warn', logger_title='Админское изменение баланса',
            logger_info=f'**{ctx.author.name}#{ctx.author.discriminator}** (`{ctx.author.id}`)' +
                        f' сбрасывает баланс для **{user.tag}** (`{user.strID}`)\n\n',
            log_to=BOT_XP_LOGS, client=self.bot
        ).send_log()

        return await ctx.send(
            f"Бан успешно произошел! Бип! Радостный буп! Шучу." +
            f"\nВы обнулили очки опыта пользователя **{user.tag}** (`{user.strID}`)."
        )


def setup(client):
    client.add_cog(Admin(client))
