import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(brief="News about the bot.")
    async def news(self, ctx):
        await ctx.send("News: From 6 july 2021 to 20 july 2021, Oahx will be offline.")
        
    @commands.command(brief="Information about the bot.")
    async def about(self, ctx):
        async with ctx.bot.embed(title="About Oahx", description=f"Hello! Im Oahx, made by `jotte, FrostiiWeeb`, this message is stuff about me.\n\n```\nGuilds: {len(ctx.bot.guilds)}\n\nUsers: {len(ctx.bot.users)}\n```") as embed:
            await embed.send(ctx.channel)
            
def setup(bot):
    bot.add_cog(Misc(bot))          