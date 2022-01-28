from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_guild_count(self, data):
        return len(self.bot.guilds)

    @ipc.server.route()
    async def get_channel_count(self, data):
        return len([channel for channel in self.bot.get_all_channels()])

    @ipc.server.route()
    async def get_user_count(self, data):
        return len(self.bot.users)


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
