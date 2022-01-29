from discord import *
from discord.ext import commands
import asyncio

"""
mounter = Mount(oahx)
mounter.mount(AloneBot(command_prefix=..., ...))
"""

class Mount():
	def __init__(self, bot : commands.Bot) -> None:
		self.bot = bot
		self.mounts = {}
		self.mount_ = 0

	async def _activate(self, mount_id : int):
		bot : commands.Bot = self.mounts.get(str(mount_id))
		self.bot._enabled = False
		bot.enabled = True
		...
		
	
	def _mount(self, bot : commands.Bot):
		self.mounts[str(self.mount_)] = bot
		self.mounts[str(self.mount_)].activate = self._activate
		self.bot.mounts = self.mounts
		self.mount_ += 1
			

	def mount(self, bot : commands.Bot):
		self._bot : commands.Bot = bot
		return self._mount(bot)