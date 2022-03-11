from ._emoji import *
from ._errors import *
from ._command import *

class Events(Emoji, Completion, Error):
	def __init__(self, bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Events(bot))