# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.UserConverter import Target

# ====================================


class Levels(commands.Cog, name='Уровни'):

    def __init__(self, client):
        self.client = client

    # ===============================

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        if message.content.startswith(BOT_PREFIX):
            return
        if message.author.id == self.client.user.id:
            return
        if message.author.bot is True:
            return

        # Отменяется скрипт, если пользователь лишён возможность получать очки опыта
        role = discord.utils.get(message.guild.roles, name="noXP")
        if role in message.author.roles:
            del role
            return
        del role

        user_id = message.author.id
        log_chan = self.client.get_channel(BOT_XP_LOGS)
        temp_embed = discord.Embed()

        # Проверка, если пользователь существует в БД
        a = await fetch_data('xp', 'user', user_id)
        if a is None:
            await add_user_into_data(user_id)
            temp_embed.description = f'Пользователь не был найден ' + \
                                     'в базе данных, но успешно внесён.'
        else:
            pass

        triggered_at = int(time.time())

        # Fetches when was edited last time
        cooldowns_at = await fetch_data('lastTimeEdited', 'user', user_id)

        # Cooldowns to prevent spamming
        if triggered_at - cooldowns_at < 90:
            return

        temp_embed.colour = 0x68B4FA
        temp_embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar_url)

        # Fetches current XP
        current_xp = await fetch_data('xp', 'user', user_id)

        temp_embed.add_field(name="Предыдущий баланс", value=current_xp)

        bonus_xp = random.randint(2, 5)
        updated_xp = current_xp + bonus_xp

        await update_data('xp', updated_xp, 'user', user_id)
        temp_embed.add_field(name="Добавлено очков", value=bonus_xp)
        del bonus_xp, updated_xp, a

        await update_data('lastTimeEdited', triggered_at, 'user', user_id)
        del triggered_at

        new_xp = await fetch_data('xp', 'user', user_id)
        temp_embed.add_field(name='Обновлённый баланс', value=new_xp)

        # !!!!!!!!! Потенциальная проблема - возможность получения ошибок 429 !!!!!!!!!
        return await log_chan.send(embed=temp_embed)

    # ===============================

    @commands.command(aliases=['lb'], brief='ТОП-5 лидеров по количеству опыта',
                      help='ТОП-5 лидеров по количеству опыта')
    @commands.guild_only()
    @commands.cooldown(1, 60, type=BucketType.guild)
    async def leaderboard(self, ctx):
        message = await ctx.send(embed=discord.Embed(
            colour=SECONDARY_COLOR,
            title=':hourglass: Подготовка таблицы...',
        ))

        temp_embed = discord.Embed()
        temp_embed.colour = 0x7289DA
        data = await fetch_top_5()
        user = None
        top_1_id = int(data[0].split(' $$$ ')[0])
        top_1_user_obj = await self.client.fetch_user(top_1_id)

        temp_embed.set_footer(
            text='%s является абсолютным лидером! Ура!' % top_1_user_obj,
            icon_url=top_1_user_obj.avatar_url
        )
        temp_embed.title = 'ТОП-5 ЛИДЕРОВ ПО БАЛАНСУ ОЧКОВ ОПЫТА'
        temp_embed.set_thumbnail(url=top_1_user_obj.avatar_url)

        for i in range(len(data)):
            temp_data = data[i].split(' $$$ ')
            user = await self.client.fetch_user(int(temp_data[0]))

            temp_embed.add_field(
                name='[#%s] ' % str(i + 1) + str(user) + ' (' + str(user.id) + ')',
                value='**' + str(temp_data[1]) + '** опыта', inline=False
            )

        await message.edit(embed=temp_embed)
        del temp_embed, user, top_1_user_obj, top_1_id, data

    @commands.command(name='xp', aliases=['rank', 'balance', 'bal'], brief='Узнать свой баланс опыта', help='Узнать свой баланс опыта')
    @commands.guild_only()
    @commands.cooldown(2, 6, type=BucketType.user)
    async def xp(self, ctx, user: discord.User = None):

        temp_embed = discord.Embed()

        if user is self.client.user:
            return await ctx.send(f"Оу. Но создатель решил, что я не могу иметь уровень! Просите. Бип. Буп.")

        if user is None:
            user = ctx.author

        if user.bot is True:
            return await ctx.send('Нет. Машинам нельзя иметь уровень.')

        user = Target(user)

        current_xp = await fetch_data('xp', 'user', user.intID)

        if current_xp is None:
            return await ctx.send(embed=discord.Embed(
                colour=0x000000, title='Ошибка',
                description='Этот пользователь не отправил ни одного сообщения с того момента, ' +
                            'как я появился на сервере, поэтому его нет в базе данных. \n\n' +
                            'Ему нужно отправить хотя бы одно сообщение, чтобы появится в ней.'))

        temp_embed.colour = 0x7289DA
        temp_embed.description = f'**{current_xp}** очков опыта'
        temp_embed.title = f'Баланс пользователя {user.tag}'
        temp_embed.set_thumbnail(url=user.avatar_url)
        temp_embed.set_footer(text=f'Запрашивает {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=temp_embed)
        temp_embed.clear_fields()
        del temp_embed
        return


def setup(client):
    client.add_cog(Levels(client))
