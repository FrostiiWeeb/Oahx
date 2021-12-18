import discord
from discord.ext import commands
import contextlib
import copy

class Application(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.group(name="application", invoke_without_command=True, breif="Application command.")
  async def application(self, ctx):
    pass

def setup(bot):
    bot.add_cog(Application(bot))
