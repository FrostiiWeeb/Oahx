import discord
from discord.ext import commands
from utils.CustomContext import CoolContext

class Alone(commands.Bot):
    def __init__(self, command_prefix, help_command=None, description=None, mount = None, **options):
        super().__init__(command_prefix, help_command, description, **options)
        self._bot : commands.Bot = mount

    @property
    def user(self):
        return self._bot.user

    async def on_message(self, message : discord.Message):
        if message.content.startswith("alone"):
            ctx = await self.get_context(message, cls=CoolContext)
            try:
                return await ctx.command.callback()
            except:
                pass
        return await self.process_commands(message)