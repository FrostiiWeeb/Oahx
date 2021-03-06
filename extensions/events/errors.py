import sys
import traceback
import datetime
import discord
import humanize
from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands import Cog
from extensions.contacts import NumberNotFound, ConnectionError
from extensions.economy import NotInDB
from utils.models import *


class ErrorEmbed(discord.Embed):
    def __init__(self, description, **kwargs):
        super().__init__(
            color=discord.Color.from_rgb(100, 53, 255),
            title="An error occurred!",
            description=description,
            timestamp=datetime.datetime.utcnow(),
        )


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.errors = {
            commands.MissingRequiredArgument: "Missing required argument(s): " "{error.param}",
            commands.MissingPermissions: "Missing required permission(s): " "{missing_perms}",
            commands.BotMissingPermissions: "I'm missing permission(s): " "{missing_perms}",
            commands.NotOwner: "You don't own this bot.",
            commands.NSFWChannelRequired: "{ctx.command} is required to be " "invoked in a NSFW channel.",
            commands.MaxConcurrencyReached: "{ctx.command} is already being " "used, please wait.",
            commands.DisabledCommand: "{ctx.command} has been disabled, please wait until it's enabled.",
            commands.BadUnionArgument: "Cannot convert Argument into int, str, etc..",
            commands.ExtensionNotFound: "The extension you provided is invalid.",
            commands.ExtensionNotLoaded: "The extension you provided has not been loaded.",
            commands.BadArgument: "Bad argument, cannot convert to int, str, discord member..",
            NumberNotFound: "{error.msg}",
            ConnectionError: "{error.msg}",
            NotInDB: "{error}",
            discord.HTTPException: None,
            commands.CommandOnCooldown: "{ctx.command.name} is on cooldown, please wait.",
        }

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, "original", error)
        description: str = None

        if isinstance(error, tuple(self.bot.errors.keys())):
            reinvokable = isinstance(
                error, (commands.MissingPermissions, commands.BotMissingPermissions)
            ) and await self.bot.is_owner(ctx.author)
            # if reinvokable:
            # return await ctx.reinvoke()
            reinvokable = isinstance(error, (commands.MissingPermissions, commands.BotMissingPermissions))
            try:
                description = str.format(self.bot.errors[type(error)], ctx=ctx, error=error)
            except KeyError:
                if reinvokable:
                    description = str.format(
                        self.bot.errors[type(error)],
                        ctx=ctx,
                        error=error,
                        missing_perms=f"{', '.join(error.missing_permissions)}",
                    )
            print(description, file=sys.stderr)
        else:
            ignored = (
                commands.CommandNotFound,
                commands.CheckFailure,
            )
            if isinstance(error, ignored):
                return
            formatted = traceback.format_exception(type(error), error, error.__traceback__)
            description = ("").join(formatted)
            print(description, file=sys.stderr)

        try:
            formatted = traceback.format_exception(type(error), error, error.__traceback__)
            await ctx.reply(embed=ErrorEmbed(description=f"```\n{description}\n```"))
        except discord.Forbidden:
            pass


def setup(bot):
    bot.add_cog(Error(bot))
