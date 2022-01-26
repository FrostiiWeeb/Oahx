import discord, time, asyncio
from discord.ext import commands
from utils.models import *
from __main__ import database


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_snipe : SnipedMessage = None

    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        await database.connect()
        self.last_snipe = SnipedMessage(message.author, message)
        await self.bot.snipes.objects.create(message_id=self.last_snipe.message.id, content=self.last_snipe.message.content)

    @commands.command("snipe")
    async def snipe(self, ctx : commands.Context):
        await database.connect()
        exe = None
        err = False
        try:
            exe = await self.bot.snipes.objects.get(message_id=self.last_snipe.message.id)
        except:
            exe = self.last_snipe
            err = True
        if err:
            return await self.last_snipe.send(exe.message.content)
        else:
            return await self.last_snipe.send(exe.content)

    @commands.command(brief="Information about the bot.")
    async def about(self, ctx):
        shard_id = ctx.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = round(shard.latency * 1000)
        shard_servers = len(
            [guild for guild in self.bot.guilds if guild.shard_id == shard_id]
        )
        async with ctx.bot.embed(
            title="About Oahx",
            description=f"Hello! Im Oahx, made by `jotte, FrostiiWeeb, MrArkon, NotFahad`, this message is stuff about me.\n\n```\nGuilds: {len(ctx.bot.guilds)}\nUsers: {len(ctx.bot.users)}\nShard [{shard_id}] Guilds: {shard_servers}\n```",
        ) as embed:
            await embed.send(ctx.channel)

    @commands.command(aliases=["ping"], brief="Get the latency of the bot")
    async def latency(self, ctx):
        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2 - time_1) * 1000)
        shard_id = ctx.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = round(shard.latency * 1000)
        shard_servers = len(
            [guild for guild in self.bot.guilds if guild.shard_id == shard_id]
        )
        msg = await ctx.send(f":ping_pong:...")
        embed = discord.Embed(
            colour=discord.Colour.blurple(),
            title="Pong!",
            description=f"Websocket latency: {round(self.bot.latency * 1000)}\nTyping latency: {ping}\nShard latency [{shard_id}]: {shard_ping}",
        )
        await asyncio.sleep(1)
        await msg.edit(embed=embed)

    @commands.command(name="source", aliases=["src"], brief="This might be a surprise.")
    async def susrc(self, ctx):
        async with ctx.bot.embed(
            title="Uhhhh",
            description="This bot is private-sourced, that means you'll have to dm FrostiiWeeb#8373 the reason you want to get access to it.",
        ) as e:
            await e.send(ctx.channel)

    @commands.command(
        name="credit", aliases=["crdit"], brief="This might be a surprise, again."
    )
    async def suscr(self, ctx):
        async with ctx.bot.embed(
            title="Uhhhh",
            description="**Oahx is property of AlePI.**\n- emoji.gg for coin emoji",
        ) as e:
            await e.send(ctx.channel)


def setup(bot):
    bot.add_cog(Misc(bot))
