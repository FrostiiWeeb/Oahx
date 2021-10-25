from typing import Literal

import discord
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx: commands.Context):
        await ctx.bot.wait_until_ready()

        prefixes: list[str] = await ctx.bot.get_prefix(ctx.message)
        description: str = "I respond to:\n\n"

        # format non-mention prefixes with ticks
        for prefix in prefixes:
            head: Literal["`", ""] = "`"
            centre: Literal["`", ""] = ""

            if prefix.startswith("<@"):
                head = ""
                centre = "`"
            description += f"{head}{prefix}{centre}help`\n"

        embed: discord.Embed = discord.Embed(
            colour=6567423,
            title="Prefix Oahx",
            description=description
        )

        await ctx.send(embed=embed)
        
        
def setup(bot):
    bot.add_cog(Information(bot))