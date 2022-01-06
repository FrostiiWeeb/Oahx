
import discord
from discord.ext import commands

class Config(commands.Cog, name="Config"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.db.execute("INSERT INTO prefixes(guild_id,prefix) VALUES($1,$2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2", guild.id, "!*")
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db.execute("DELETE FROM prefixes WHERE guild_id = $1", guild.id)


def setup(bot):
	bot.add_cog(Config(bot))