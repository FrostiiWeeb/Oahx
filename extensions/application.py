import discord
from discord.ext import commands
import contextlib
import copy, string, random

class Application(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.group(name="application", invoke_without_command=True, breif="Application command.")
  async def application(self, ctx):
    pass

  @application.command(name="apply")
  async def application_apply(self, ctx):
    questions = [
      "Why do you wanna join our staff team?",
      "Why should we choose you?",
      "How will you help us?",
      "Are you gonna follow all of our rules?"

    ]
    answers = [

    ]
    for i in questions:
      await ctx.send(i)

      answer = await self.bot.wait_for("message", check=lambda msg : msg.author == ctx.author and msg.channel == ctx.channel)
      answers.append(answer)
    await ctx.send("We have received your application, we will review it soon.")
    code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    why_staff = answers[0]
    why_choose_you = answers[1]
    follow_rule = answers[3]
    how_help = answers[2]
    await self.bot.db.execute("INNSERT INTO application(id, guild_id, channel_id, why_staff, why_choose_you, follow_rule, how_help) VALUES ($1, $2, $3, $4, $5, $6, $7)", code, answer.guild.id, answer.channel.id, answers[0], answers[1], answers[3], answers[2])
    await ctx.send(", ".join([why_staff, why_choose_you, follow_rule, how_help]))
def setup(bot):
    bot.add_cog(Application(bot))
