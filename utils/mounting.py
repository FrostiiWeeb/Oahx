from discord import *
from discord.ext import commands
import asyncio

"""
mounter = Mount(oahx)
mounter.mount(AloneBot(command_prefix=..., ...))
"""


class Mount:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.mounts = {}
        self.mount_ = 0
        bot.mounts = {}

    def _mount(self, bot: commands.Bot):
        self.mounts[self.mount_] = bot
        self.bot.mounts[self.mount_] = bot
        self.bot.mounts = self.mounts
        self.mount_ += 1

    def mount(self, bot: commands.Bot):
        self._bot: commands.Bot = bot
        return self._mount(bot)
