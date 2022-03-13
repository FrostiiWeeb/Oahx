from .information import Information
from discord.ext import commands

class Configuration(Information):
	def __init__(self, bot: commands.Bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Configuration(bot))