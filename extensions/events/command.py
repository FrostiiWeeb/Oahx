from discord.ext import commands
import discord

class Completion(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_completion(self, context: commands.Context):
		bot = context.bot
		db = context.bot.db
		old_db = await bot.db.fetchrow("SELECT count FROM ran_total_commands")
		new_count = old_db["count"] + 1
		await db.execute("UPDATE ran_total_commands SET count = $1", new_count)