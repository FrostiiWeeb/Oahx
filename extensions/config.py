import discord
from discord.ext import commands


class Config(commands.Cog, name="Config"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.redis.hset("prefixes", guild.name, "oahx ")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.redis.delete("prefixes", guild.name)


def setup(bot):
    bot.add_cog(Config(bot))
