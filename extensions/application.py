import discord
from discord.ext import commands
import contextlib
import copy

class Application(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

def setup(bot):
    bot.add_cog(Application(bot))
