# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from discord.ext import commands
from Twig.TwigCore import *
from Twig.Utils.UserConverter import Target
from Twig.Utils.HugMessages import HugMessages, do_hug


# ====================================


# MAINTAINER CHECKER
def check_if_maintainer(ctx):
    return ctx.author.id in BOT_MAINTAINERS


class Utils(commands.Cog, name='Разное'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='hug', aliases=['обнять'], brief='Позволяет делать обнимашки с:')
    @commands.cooldown(3, 10, type=BucketType.user)
    async def _hug(self, ctx, target: discord.User):
        target = Target(target)
        sender = ctx.author
        sender = Target(sender)
        msg = do_hug(target.mention, sender.tag)
        del target, sender
        return await ctx.send(msg)

    @commands.command(brief='Pong!', help='Pong!')
    @commands.cooldown(1, 5, type=BucketType.guild)
    async def ping(self, ctx):
        t1 = time.perf_counter()
        message = await ctx.send(":ping_pong:")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.client.latency * 1000, 2)
        await message.edit(content=f":ping_pong: Задержка отправки запросов составляет **{rest}мс** | " +
                                   f"Задержка «сердцебияния» составляет **{latency}мс**")

    @commands.command(name="voicedemo", aliases=['voiceshare', 'vd', 'vcss', 'vcdemo'],
                      brief='Получить ссылку для включения демонстрации экрана')
    @commands.cooldown(1, 20, type=BucketType.user)
    async def _voicedemo(self, ctx, channel=None):
        if channel is None:
            return await ctx.send(embed=
            discord.Embed(
                title=':warning: Операция прервана!',
                description='Вы не указали ID голосового канала.',
                colour=0xF1C41F)
            )

        await self.client.fetch_channel(int(channel))
        channel = self.client.get_channel(int(channel))

        return await ctx.send(embed=discord.Embed(
            colour=0x2ECC71,
            title=':desktop: Демонстрация экрана для канала %s'
                  % channel,
            description='[→ Приступить к работе](%s)'
                        % ('https://discordapp.com/channels/' + str(ctx.guild.id) + '/' + str(channel.id))
        ))

    @commands.command(name='userinfo', aliases=['info'], brief='Информация о пользователях')
    @commands.cooldown(3, 30, type=BucketType.user)
    async def _userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = member = ctx.author
            user = await self.client.fetch_user(user.id)
        else:
            member = None if ctx.guild is None else ctx.guild.get_member(user.id)

        embed = discord.Embed()
        try:

            if user.bot is True:
                bot_or_not = 'Да'
            else:
                bot_or_not = 'Нет'

            if user.id in BOT_MAINTAINERS:
                embed.description = ':heart: Этот пользователь поддерживает моё существование!'

            embed.colour = DEFAULT_COLOR
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name='Имя пользователя', value=f'{user.name}#{user.discriminator}')
            embed.add_field(name='Идентификатор', value=str(user.id))
            embed.add_field(name='Бот?', value=bot_or_not)
            embed.add_field(name='Ссылка на аватар', value=f'[Перейти по ссылке]({user.avatar_url})')

            if member is not None:
                embed.colour = member.top_role.colour

                member_status = str(member.status)

                if member_status == 'online':
                    member_status = 'В сети'
                elif member_status == 'dnd':
                    member_status = 'Не беспокоить'
                elif member_status == 'idle':
                    member_status = 'Нет на месте'
                elif member_status == 'offline':
                    member_status = 'Не в сети'

                embed.add_field(name='Статус', value=member_status)

                if member.activity is not None:
                    if member.activity.type == discord.ActivityType.playing:
                        embed.add_field(name='Активность', value=f'Играет в {member.activity.name}')
                    elif member.activity.type == discord.ActivityType.streaming:
                        embed.add_field(name='Активность', value=f'Стримит {member.activity.name}')
                    elif member.activity.type == discord.ActivityType.watching:
                        embed.add_field(name='Активность', value=f'Смотрит {member.activity.name}')
                    elif member.activity.type == discord.ActivityType.listening:
                        embed.add_field(name='Активность', value=f'Слушает {member.activity.title}')
                    else:
                        embed.add_field(name='Активность', value='Неизвестно')

                embed.add_field(name='Присоединился в',
                                value=f'`{member.joined_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`', inline=False)

            embed.add_field(name='Аккаунт создан в',
                            value=f'`{user.created_at.strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")} (UTC)`', inline=False)

        except:
            pass

        return await ctx.send(embed=embed)

    @commands.command(aliases=['bot_info'], brief='Проверить информацию о боте', help='Проверить информацию о боте')
    @commands.cooldown(1, 30, type=BucketType.guild)
    async def about(self, ctx):
        try:
            uptime = time.time() - BOT_STARTED_AT
            uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime))
            guilds_number = str(len(self.client.guilds))
            users_total = str(len(await fetch_whole_table()))

            creator = self.client.get_user(576322791129743361)

            repo = git.Repo(".git")
            commit = repo.head.commit
            sha = repo.head.object.hexsha
            short_sha = repo.git.rev_parse(sha, short=7)

            temp_embed_desc = f':wave: Привет! Я {self.client.user.name}!\n' + \
                              'Я бот, который подсчитывает опыт.\n\n' + \
                              '**Немного статистики:**\n' + \
                              '• Считаю опыт на %s серверах\n' % guilds_number + \
                              '• Уже знаю %s человека\n\n' % users_total

            temp_embed = discord.Embed()
            temp_embed.colour = 0xF7EE91
            temp_embed.add_field(name='Версия', value='`%s`' % short_sha, inline=True)
            temp_embed.add_field(name='Аптайм', value='`%s`' % str(uptime), inline=True)
            temp_embed.add_field(name='GitHub Репозиторий',
                                 value="[Перейти по ссылке](https://github.com/runic-tears/twig-bot)", inline=True)
            temp_embed.add_field(name='Меня создал', value='`%s (%s)`' % (str(creator), str(creator.id)), inline=True)
            temp_embed.set_footer(text='Запрашивает %s (%s)' % (ctx.author, ctx.author.id),
                                  icon_url=ctx.author.avatar_url)
            temp_embed.description = temp_embed_desc
            temp_embed.title = f'{self.client.user.name}'

            await ctx.send(embed=temp_embed)
            del uptime, temp_embed, commit, repo, sha, short_sha, guilds_number, users_total, temp_embed_desc
        except Exception as err:
            await ctx.send('Ошибка! ' + '```' + str(err) + '```')
            raise err


def setup(client):
    client.add_cog(Utils(client))
