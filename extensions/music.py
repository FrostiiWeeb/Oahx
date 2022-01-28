"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re

import discord
from discord.ext import commands
import slate
import slate.obsidian
import yarl

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
    
        self.bot = bot
        self.slate = slate.obsidian.NodePool()

    async def load(self) -> None:

        await self.slate.create_node(
            bot=self.bot,
            identifier="ObsidianNode01",
            host="127.0.0.1",
            port="3030",
            password="",
        )

        print("Slate is connected!")

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await ctx.send(str(error))

    @commands.command(name="join")
    async def join(self, ctx: commands.Context) -> None:

        if ctx.voice_client and ctx.voice_client.is_connected():
            raise commands.CommandError(
                f"I am already connected to {ctx.voice_client.channel.mention}."
            )

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError(
                "You must be connected to a voice channel to use this command."
            )

        await ctx.author.voice.channel.connect(cls=slate.obsidian.Player)
        await ctx.send(f"Joined the voice channel {ctx.voice_client.channel.mention}.")

    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, search: str) -> None:

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            await ctx.invoke(self.join)

        url = yarl.URL(search)
        if url.scheme and url.host:
            source = slate.Source.NONE
        else:
            source = slate.Source.YOUTUBE

        try:
            result = await ctx.voice_client._node.search(search, source=source, ctx=ctx)
        except slate.NoResultsFound:
            raise commands.CommandError(
                "No results were found for your search."
            )
        except slate.HTTPError:
            raise commands.CommandError(
                "There was an error while searching for results."
            )

        await ctx.voice_client.play(result.tracks[0])
        await ctx.send(f"Now playing: **{result.tracks[0].title}** by **{result.tracks[0].author}**")

    @commands.command(name="disconnect")
    async def disconnect(self, ctx: commands.Context) -> None:

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise commands.CommandError(
                "I am not connected to any voice channels."
            )
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError(
                "You must be connected to a voice channel to use this command."
            )
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            raise commands.CommandError(
                f"You must be connected to {ctx.voice_client.channel.mention} to use this command."
            )

        await ctx.send(f"Left {ctx.voice_client.channel.mention}.")
        await ctx.voice_client.disconnect()

def setup(bot):
    bot.add_cog(Music(bot))
