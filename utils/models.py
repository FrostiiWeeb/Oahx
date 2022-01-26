import typing, discord

class SnipedMessage:
	__slots__ = ('author', 'snipe_before', 'snipe_after', 'message')

	def __init__(self, author : typing.Union[discord.User, discord.Member], message : discord.Message, snipe_before = None, snipe_after = None):
		self.author = author
		self.message = message
		self.snipe_before = snipe_before
		self.snipe_after = snipe_after

	async def reply(self, *args, **kwargs):
		return await self.message.reply(*args,**kwargs)
	
	async def send(self, *args, **kwargs):
		return await self.message.channel.send(*args,**kwargs)