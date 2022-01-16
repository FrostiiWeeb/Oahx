from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_guild_count(self, data):
        return len(self.bot.guilds)


def setup(bot):
    bot.add_cog(IpcRoutes(bot))