from dotenv import load_dotenv, dotenv_values
from discord.ext.commands import BucketType
from contextlib import redirect_stdout
from Twig.Workers.Configurator import *
# from Twig.SQL.Functionality import *
from Twig.SQL.AsyncFunctionality import *
import pathlib
import datetime
import aiohttp
import asyncio
import discord
import logging
import time
import json
import io
import os
import git
import sys
import re
import textwrap
import traceback
import random

env_path = pathlib.Path('./config/token.env')
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("TOKEN")

ERROR_COLOR = 0xDD2E44
SUCCESS_COLOR = 0x77B255
SECONDARY_COLOR = 0x3B88C3
DEFAULT_COLOR = discord.Colour.default()
WARNING_COLOR = discord.Colour.gold()
BLURPLE_COLOR = discord.Colour.blurple()

print('[CORE:BADGUY] Imports are ready!')
