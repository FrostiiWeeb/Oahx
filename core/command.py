import typing
import discord

from discord.ext import commands
from utils.CustomContext import CoolContext


class BaseCommand:
	def __init__(self, name : str, help : str) -> None:
		self.name = name
		self.help = help

	def _parse(self, message: discord.Message):
		if message.author.bot:
			...
			
	async def callback(self):
		raise NotImplementedError

class Command(BaseCommand):
	...