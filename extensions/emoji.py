import discord
from discord.ext import commands


class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def emoji(self, msg):
        if msg.content.endswith(";"):
            if msg.author.id in self.bot.mods:
                emj_name = msg.content.strip(";")
                for g in self.bot.guilds:
                    for emj in g.emojis:
                        if emj_name == emj.name:
                            return await msg.channel.send(str(emj))


def setup(bot):
    bot.add_cog(Emoji(bot))
