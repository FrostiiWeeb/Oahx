from discord.ext import commands
import discord, asyncio, time


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c"])
    async def cookie(self, ctx):
        """
        Cookie command!
        """

        def check(reaction, user):
            return str(reaction.emoji) == "🍪" and user != ctx.me

        try:
            start = time.perf_counter()
            msg = await ctx.send(embed=discord.Embed(title="Get the :cookie:!", description="Go!"))
            await msg.add_reaction("🍪")
            reaction, user = await self.bot.wait_for("reaction_add", timeout=20.0, check=check)
            if str(reaction.emoji) == "🍪":
                end = time.perf_counter()
                embed = discord.Embed(
                    title=user.name,
                    description=f"This fool took {round(end-start, 2)} seconds.",
                )
                await msg.edit(embed=embed)
        except asyncio.TimeoutError:
            return


def setup(bot):
    bot.add_cog(Fun(bot))
