import discord
from discord.ext import commands


class Target:
    def __init__(self, user_obj: discord.User = None):
        self.original = user_obj                           # Оригинальный объект
        self.intID = user_obj.id                           # Дефолтное значение - integer
        self.strID = str(user_obj.id)                      # Преобразование intID в строку
        self.name = str(user_obj.name)                     # Получение имени
        self.discrim = str(user_obj.discriminator)         # Получить дискриминатор
        self.tag = str(self.name + '#' + self.discrim)     # Получить тэг в виде строки, а не объекта
        self.mention = user_obj.mention                    # Создать упоминание
        self.bot = user_obj.bot                            # Алиас user.bot
        self.avatar_url = user_obj.avatar_url              # Алиас discord.user.avatar_url
