from ast import _identifier
import wavelink
import discord
import re

from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.wavelink = bot.wavelink
	
    async def connect_nodes(self):
        await self.wavelink.create_node(bot=self.bot,
                                            host='127.0.0.1',
                                            port=1983,
                                            password='oahx_lavalink', identifier="Oahx Player 1")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')


    @commands.command(name="join", aliases=["connect"])
    async def join(
        self, ctx: commands.Context, *, channel: discord.TextChannel = None
    ) -> None:

        if not channel:
            channel = getattr(ctx.author.voice, "channel", None)
            if not channel:
                raise commands.CheckFailure(
                    "You must be in a voice channel to use this command"
                    "without specifying the channel argument."
                )

        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        await ctx.send(f"Joined the voice channel `{channel}`")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str) -> None:

        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client
        await player.play(search)

def setup(bot):
	bot.add_cog(Music(bot))