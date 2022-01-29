import wavelink
import discord
import re

from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.pomice = bot.wavelink

    @commands.Cog.listener("on_node_ready")
    async def node_ready(self, node):
        print("Node {.identifier} is ready.".format(node))

    async def connect_nodes(self):
        await self.pomice.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port="1983",
            password="oahx_lavalink",
            identifier="Node 1",
        )
        self.bot.dispatch("node_ready", node=self.wavelink.nodes.get("Node 1"))

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
    async def play(self, ctx, *, search: wavelink.YouTubeTrack) -> None:
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client
        """
		results = await player.get_tracks(query=f"{search}")
		if not results:
			raise commands.CommandError("No results were found for that search term.")
		if isinstance(results, .Playlist):
			await player.play(track=results.tracks[0])
		"""
        await player.play(search)


def setup(bot):
    bot.add_cog(Music(bot))
