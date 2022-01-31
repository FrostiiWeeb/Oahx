import discord
from discord.ext import commands
from utils.CustomContext import CoolContext
from discord.http import HTTPClient
import asyncio
from utils.models import Client


class BaseAlone(commands.Bot, Client):
	pass
class Alone(commands.Bot):
	def __init__(self, command_prefix, help_command=None, description=None, mount = None, **options):
		super().__init__(command_prefix, help_command, description, **options)
		self._bot : commands.Bot = mount
		
		
	async def on_message(self, message : discord.Message):
		return await self.process_commands(message)