from ._emoji import *
from ._errors import *

class Events(Emoji, Error):
	def __init__(self, bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Events(bot))