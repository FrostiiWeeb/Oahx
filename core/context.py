import discord

import typing
from discord.ext import commands
from .command import Command


class Context:
    def __init__(self, bot: commands.Bot, channel: discord.TextChannel, message: discord.Message) -> None:
        self.bot = bot
        self.channel = channel
        self.message = message

    async def send(self, *args, **kwargs):
        return await self.channel.send(*args, **kwargs)

    async def reply(self, *args, **kwargs):
        return await self.message.reply(*args, **kwargs)
