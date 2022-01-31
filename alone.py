import discord
from discord.ext import commands
from utils.CustomContext import CoolContext
from discord.http import HTTPClient
import asyncio

class Alone(commands.Bot):
	def __init__(self, command_prefix, help_command=None, description=None, mount = None, **options):
		super().__init__(command_prefix, help_command, description, **options)
		self._bot : commands.Bot = mount
		self.http = HTTPClient()
		self.user_pay = None

	@property
	def user(self):
		return self._bot._connection.user

	async def get_user(self):
		if self.user_pay:
			self._user = discord.user.ClientUser(state="online", data=self.user_pay)
		else:
			self.user_pay = await self.http.static_login(self._bot.http.token)
			return await self.get_user()
		return self._user
		
		
	async def on_message(self, message : discord.Message):
		await self.get_user()
		if message.content.startswith("a!"):
			ctx = await self.get_context(message, cls=CoolContext)
			try:
				return await ctx.command.callback()
			except:
				pass
		return await self.process_commands(message)