from ._emoji import Emoji
from ._errors import Error
from ._command import Completion

class Events(Emoji, Error, Completion):
	def __init__(self, bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Events(bot))