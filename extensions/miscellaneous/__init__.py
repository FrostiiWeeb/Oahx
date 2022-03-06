from ._misc import Misc

class Miscellaneous(Misc):
	def __init__(self, bot):
		super().__init__(bot)

def setup(bot):
	bot.add_cog(Miscellaneous(bot))