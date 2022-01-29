import wavelink
import discord
import re

from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.wavelink = bot.wavelink
	
    async def connct_nodes(self):
        await self.wavelink.create_node(bot=self.bot,
                                            host='127.0.0.1',
                                            port=1983,
                                            password='oahx_lavalink')

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

        await ctx.author.voice.channel.connect(cls=pomice.Player)
        await ctx.send(f"Joined the voice channel `{channel}`")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str) -> None:

        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client

        results = await player.get_tracks(query=f"{search}")

        if not results:
            raise commands.CommandError("No results were found for that search term.")

        if isinstance(results, pomice.Playlist):
            await player.play(track=results.tracks[0])
        else:
            await player.play(track=results[0])

def setup(bot):
	bot.add_cog(Music(bot))