from .contacts import *
from discord.ext import commands

class Phone(Contacts):
	def __init__(self, bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Phone(bot))