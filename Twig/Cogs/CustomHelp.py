# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ====================================
from discord.ext import commands


# ====================================


class MyHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return 'Используйте {0.clean_prefix}help <команда>, '.format(self) + \
               'чтобы узнать подробнее об этой команде.'


class CustomHelp(commands.Cog, name='Помощь'):
    def __init__(self, client):
        self._original_help_command = client.help_command
        client.help_command = MyHelpCommand(indent=1, no_category='Без Категории')
        client.help_command.cog = self

    # def cog_unload(self):
    #     self.bot.help_command = self._original_help_command


def setup(client):
    client.add_cog(CustomHelp(client))
