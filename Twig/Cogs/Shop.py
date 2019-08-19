# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from discord.ext import commands
from Twig.TwigCore import *


# ====================================


# MAINTAINER CHECKER
def check_if_maintainer(ctx):
    return ctx.author.id in BOT_MAINTAINERS


class Shop(commands.Cog, name='Магазинчик'):

    def __init__(self, client):
        self.client = client

    async def roles_shop_embed(self, ctx):
        message = await ctx.send(embed=discord.Embed(
            title=':hourglass: Загрузка...',
            description='Подождите немного, сейчас всё будет!',
            colour=SECONDARY_COLOR
        ))

        await asyncio.sleep(0.2)

        try:
            with open('config/' + str(ctx.guild.id) + '/levels.json') as r:
                levels = json.load(r)
        except Exception as err:
            return await message.edit(embed=discord.Embed(
                title=':x: Ошибка!',
                description='Вам лучше передать это разработчику: \n\n{}'.format(str(err)),
                colour=ERROR_COLOR,
            ))

        temp_embed = discord.Embed(title='Магазин ролей')
        temp_embed.colour = BLURPLE_COLOR
        temp_embed.set_footer(
            text=f'Чтобы купить роль, используйте: {BOT_PREFIX}shop buy <тип_товара> <код_товара>')
        description_data = ''

        for level, parameters in levels.items():
            shop_id = parameters['shop_id']
            role_id = parameters['role']
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            price = parameters['price']

            description_data = \
                description_data + f'[#{shop_id}] {role.mention}\n **Цена:** {price} очков опыта\n**Купить:** `{BOT_PREFIX}shop buy roles {shop_id}` \n\n'

        temp_embed.description = description_data
        await message.edit(embed=temp_embed)

    @commands.group(name='shop')
    @commands.guild_only()
    async def _shop(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                f'Выберите отдел магазина! `{BOT_PREFIX}shop roles` - для ролей, и `{BOT_PREFIX}shop things` - для чего-то другого с:')

    @_shop.command(name='roles')
    @commands.cooldown(1, 25, type=BucketType.user)
    @commands.guild_only()
    async def _roles(self, ctx):
        return await self.roles_shop_embed(ctx)

    @_shop.command(name='things')
    @commands.cooldown(1, 25, type=BucketType.user)
    @commands.guild_only()
    async def _things(self, ctx):
        await ctx.send('Извините, но тут пусто!')

    @_shop.group(name='buy')
    @commands.cooldown(1, 25, type=BucketType.user)
    @commands.guild_only()
    async def _buy(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('Вы не указали, что вы хотите покупать - роли или вещи')

    @_buy.command(name='roles')
    @commands.cooldown(1, 25, type=BucketType.user)
    @commands.guild_only()
    async def buy_roles(self, ctx, shop_id=None):
        if shop_id is None:
            return await ctx.send('Вы не указали код товара.')

        message = await ctx.send(embed=discord.Embed(
            title=':repeat: Подождите немного...',
            description='Мне нужно кое-что проверить и подправить некоторую информацию в базе данных...',
            colour=SECONDARY_COLOR
        ))

        temp = await fetch_data('user', 'user', ctx.author.id)
        if temp is None:
            del temp
            return await message.edit(embed=discord.Embed(
                title=':x: Похоже, что вас нет в базе данных!',
                colour=ERROR_COLOR
            ))

        try:
            with open('config/' + str(ctx.guild.id) + '/levels.json') as r:
                levels = json.load(r)
        except Exception as err:
            return await message.edit(embed=discord.Embed(
                title=':x: Ошибка!',
                description='Вам лучше передать это разработчику: \n\n{}'.format(str(err)),
                colour=ERROR_COLOR,
            ))

        shop_id = int(shop_id)
        author = ctx.author

        if shop_id > len(levels) or shop_id < 1:
            return await message.edit(embed=discord.Embed(
                title=':x: Ошибка!',
                description='Я не знаю роли с таким кодом.',
                colour=ERROR_COLOR
            ))

        for level, parameters in levels.items():
            shop__id = parameters['shop_id']
            role = discord.utils.get(ctx.guild.roles, id=parameters['role'])
            price = parameters['price']

            if int(shop_id) == shop__id:
                for prev_level, prev_params in levels.items():
                    prev_shop_id = prev_params['shop_id']

                    if shop_id == 1:
                        pass
                    elif prev_shop_id == (shop_id - 1):
                        prev_role = discord.utils.get(ctx.guild.roles, id=prev_params['role'])
                        prev_price = prev_params['price']

                        if prev_role not in author.roles:
                            return await message.edit(embed=discord.Embed(
                                colour=ERROR_COLOR,
                                title=':x: Ошибка!',
                                description=f'Чтобы купить [#{shop__id}] {role.mention}, вы должны сначала купить [#{prev_shop_id}] {prev_role.mention}.'
                            ))

                author_balance = await fetch_data('xp', 'user', author.id)
                if author_balance < price:
                    price_diff = price - author_balance
                    del author_balance
                    return await message.edit(embed=discord.Embed(
                        colour=ERROR_COLOR,
                        title=':x: Ошибка!',
                        description=f'Вам не хватает {price_diff} очков опыта, чтобы купить эту роль.'
                    ))

                elif role in author.roles:
                    del author_balance
                    return await message.edit(embed=discord.Embed(
                        colour=ERROR_COLOR,
                        title=':x: Ошибка!',
                        description='У вас уже есть эта роль!'
                    ))

                await author.add_roles(role)
                author_new_balance = int(author_balance) - int(price)
                await update_data('xp', author_new_balance, 'user', author.id)

                log_chan = self.client.get_channel(BOT_XP_LOGS)
                await log_chan.send(embed=discord.Embed(
                    timestamp=datetime.datetime.utcnow(),
                    colour=role.colour
                ).set_author(
                    name=f'{author} ({author.id}) покупает роль', icon_url=author.avatar_url
                ).add_field(
                    name='Купленная роль', value=f'{role.mention} (`{role.id}`)'
                ).add_field(
                    name='Потрачено опыта', value=f'**{price}** опыта'
                ).add_field(
                    name='Предыдущий баланс', value=f'**{author_balance}** опыта'
                ).add_field(
                    name='Баланс после покупки', value=f'**{author_new_balance}** опыта'
                ))

                return await message.edit(embed=discord.Embed(
                    colour=role.color,
                    title='Наслаждайтесь!',
                    description=f'Вы успешно купили {role.mention}!'
                ))
            else:
                pass
        return

    @_buy.command(name='things', enabled=False)
    @commands.cooldown(1, 25, type=BucketType.user)
    @commands.guild_only()
    async def buy_things(self, ctx):
        return await ctx.send('Покупка шняги')


def setup(client):
    client.add_cog(Shop(client))
