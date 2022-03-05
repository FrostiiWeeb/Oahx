import discord

from discord.ext import commands

from typing import *

from bot import Oahx

class Extension(commands.Cog):
	def __init__(self, bot: Oahx) -> None:
		self.bot = bot

class Loader:
	def __init__(self, bot: Oahx) -> None:
		self.bot = bot

	def load(self, ext: Extension):
		self.bot.add_cog(ext)