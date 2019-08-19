from Twig.TwigCore import SECONDARY_COLOR, WARNING_COLOR, ERROR_COLOR, DEFAULT_COLOR, SUCCESS_COLOR
import discord
import datetime


class Logger:
    def __init__(self,
                 logger_type='info',
                 logger_title=None,
                 logger_footer=None,
                 logger_info=None,
                 logger_timestamp=True,
                 log_to=None,
                 client=None):
        self.type = logger_type
        self.title = logger_title
        self.footer = logger_footer
        self.info = logger_info
        self.client = client
        self.log_to = log_to
        self.timestamp = logger_timestamp

    async def send_log(self):
        log_embed = discord.Embed(
            title=self.title,
            description=self.info
        )

        if self.type == 'info':
            log_embed.colour = SECONDARY_COLOR
        elif self.type == 'warn':
            log_embed.colour = WARNING_COLOR
        elif self.type == 'err':
            log_embed.colour = ERROR_COLOR
        elif self.type == 'success':
            log_embed.colour = SUCCESS_COLOR
        else:
            log_embed.colour = DEFAULT_COLOR

        if self.timestamp is True:
            log_embed.timestamp = datetime.datetime.utcnow()

        if self.footer is not None:
            log_embed.set_footer(text=str(self.footer))

        channel = discord.Client.get_channel(self.client, self.log_to)
        return await channel.send(embed=log_embed)
