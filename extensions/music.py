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
import yarl
import pomice

URL_REG = re.compile(r'https?://(?:www\.)?.+')

class FakeBot():
	def __init__(self, bot) -> None:
		self.bot = bot
		self.user = discord.user.ClientUser(state=discord.state.ConnectionState(dispatch=bot.dispatch, handlers=[], hooks=[], http=bot.http, loop=bot.loop), data={'id': '844213992955707452', 'username': 'Oahx', 'avatar': '68ce329c58840bcd9bd3ee9061542c43', 'discriminator': '7757', 'public_flags': 0, 'bot': True, 'banner': None, 'banner_color': None, 'accent_color': None})

	def add_listener(self, *args, **kwargs):
		return self.bot.add_listener(*args, **kwargs)

	async def wait_until_ready(self):
		return await self.bot.wait_until_ready()
class Music(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self._fake_bot = FakeBot(bot=bot)
        
		
        self.pomice = pomice.NodePool()
    
    async def start_nodes(self):
        await self.pomice.create_node(bot=self._fake_bot, host='127.0.0.1', port='2333', 
                                     password='youshallnotpass', identifier='MAIN')
        print(f"Node is ready!")


        
    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None) -> None:
        
        if not channel:
            channel = getattr(ctx.author.voice, 'channel', None)
            if not channel:
                raise commands.CheckFailure('You must be in a voice channel to use this command'
                                            'without specifying the channel argument.')

        
        await ctx.author.voice.channel.connect(cls=pomice.Player)
        await ctx.send(f'Joined the voice channel `{channel}`')
        
    @commands.command(name='play')
    async def play(self, ctx, *, search: str) -> None:
        
        if not ctx.voice_client:
            await ctx.invoke(self.join) 

        player = ctx.voice_client        

        results = await player.get_tracks(query=f'{search}')
        
        if not results:
            raise commands.CommandError('No results were found for that search term.')
        
        if isinstance(results, pomice.Playlist):
            await player.play(track=results.tracks[0])
        else:
            await player.play(track=results[0])

def setup(bot):
    bot.add_cog(Music(bot))
