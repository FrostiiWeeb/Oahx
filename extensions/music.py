
import pomice
import discord
import re

from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")


class Nodes(dict):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

class Node():
	def __init__(self, identifier):
		self.identifier = identifier

class Music(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		self.pomice = bot.pomice
		self.nodes = Nodes()

	@commands.Cog.listener("on_node_ready")
	async def node_ready(self, node):
		print(f"Node: <{node.identifier}> is ready.")

	async def start_nodes(self):
		await self.pomice.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port="1983",
            password="oahx_lavalink",
            identifier="Node 1",
        )
		self.nodes["Node 1"] = Node("Node 1")
		print(f"Node is ready!")
		self.bot.dispatch("node_ready", node=self.nodes.get("Node 1"))

	@commands.command(name="leave", aliases=["disconnect", "dc"])
	async def leave(self, ctx: commands.Context) -> None:
        
		channel = getattr(ctx.author.voice, "channel", None)
		if not channel:
			raise commands.CommandError(
                    "You must be in a voice channel to use this command"
                )
			
		await ctx.voice_client.disconnect()
		await ctx.send(f"Disconnected the voice channel `{channel}`")

	@commands.command(name="join", aliases=["connect"])
	async def join(
        self, ctx: commands.Context, *, channel: discord.TextChannel = None
    ) -> None:
		if not channel:
        
			channel = getattr(ctx.author.voice, "channel", None)
			if not channel:
				raise commands.CommandError(
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
