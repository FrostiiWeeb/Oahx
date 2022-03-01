import discord, time, asyncio
from discord.ext import commands
from pydantic import NoneBytes
from utils.models import *
from __main__ import database


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_snipe: SnipedMessage = None

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await database.connect()
        print(before, after)
        self.last_snipe = SnipedMessage(after.author, before, snipe_before=before.content, snipe_after=after.content)
        await self.bot.editsnipes.objects.create(
            message_id=before.id,
            before_content=before.content,
            after_content=after.content,
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await database.connect()
        self.last_snipe = SnipedMessage(message.author, message)
        await self.bot.snipes.objects.create(
            message_id=self.last_snipe.message.id,
            content=self.last_snipe.message.content,
        )

    @commands.group("snipe", invoke_without_command=True)
    async def snipe(self, ctx: commands.Context, snipe_id: int = None):
        await database.connect()
        exe = None
        err = False
        try:
            exe = await self.bot.snipes.objects.get(pk=snipe_id or self.last_snipe.message.id)
        except:
            exe = self.last_snipe
            err = True
        if err:
            return await self.last_snipe.send(exe.message.content)
        else:
            return await self.last_snipe.send(exe.content)

    @snipe.command("edit")
    async def snipe_edit(self, ctx, snipe_id: int = None):
        await database.connect()
        snipe = self.last_snipe
        id = snipe_id or len(await self.bot.editsnipes.objects.all())
        snipe = await self.bot.editsnipes.objects.get(message_id=id)
        async with ctx.bot.embed(
            title="Snipe",
            description=f"<:branch:935908907715555378>**Snipe Before:**\n```\n{discord.utils.escape_markdown(snipe.before_content)}\n```\n**<:branch:935908907715555378>Snipe After:**\n```\n{discord.utils.escape_markdown(snipe.after_content)}\n```\n\n**<:branch:935908907715555378>Message From:\n```\nWIP\n```",
        ) as embed:
            await embed.send(ctx.channel)

    @commands.command(brief="Information about the bot.")
    async def about(self, ctx):
        shard_id = ctx.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = round(shard.latency * 1000)
        shard_servers = len([guild for guild in self.bot.guilds if guild.shard_id == shard_id])
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
        shard_servers = len([guild for guild in self.bot.guilds if guild.shard_id == shard_id])
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

    @commands.command(name="credit", aliases=["crdit"], brief="This might be a surprise, again.")
    async def suscr(self, ctx):
        async with ctx.bot.embed(
            title="Uhhhh",
            description="**Oahx is property of AlePI.**\n- emoji.gg for coin emoji",
        ) as e:
            await e.send(ctx.channel)


def setup(bot):
    bot.add_cog(Misc(bot))
