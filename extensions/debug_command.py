import discord
from discord.ext import commands
import sys
import typing
import humanize
from jishaku.modules import package_version
from jishaku.paginators import PaginatorInterface
from jishaku.features.baseclass import Feature
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES
from jishaku import *
from jishaku.features import *
from jishaku.flags import *
from jishaku.repl import *
from jishaku.codeblocks import *
from jishaku.exception_handling import ReplResponseReactor
import jishaku

try:
    import psutil
except ImportError:
    psutil = None


class CustomDebugCog(*STANDARD_FEATURES, *OPTIONAL_FEATURES):
    @Feature.Command(
        name="jishaku",
        aliases=["jsk"],
        hidden=True,
        invoke_without_command=True,
        ignore_extra=False,
    )
    async def jsk(self, ctx: commands.Context):  # pylint: disable=too-many-branches
        """
        The Jishaku debug and diagnostic commands.

        This command on its own gives a status brief.
        All other functionality is within its subcommands.
        """
        _bot = ctx.bot._bot
        ctx.bot = _bot
        summary = [
            f"Oahx-Jishaku 2.0.0, discord.py `{package_version('discord.py')}`, `Python {sys.version}`",
        ]

        # detect if [procinfo] feature is installed
        if psutil:
            try:
                proc = psutil.Process()

                with proc.oneshot():
                    try:
                        mem = proc.memory_full_info()
                        summary.append(
                            f"Using {humanize.naturalsize(mem.rss)} physical memory and "
                            f"{humanize.naturalsize(mem.vms)} virtual memory, "
                            f"{humanize.naturalsize(mem.uss)} of which unique to this process."
                        )
                    except psutil.AccessDenied:
                        pass

                    try:
                        name = proc.name()
                        pid = proc.pid
                        thread_count = proc.num_threads()

                        summary.append(f"Running on PID {pid} (`{name}`) with {thread_count} thread(s).")
                    except psutil.AccessDenied:
                        pass

                    summary.append("")  # blank line
            except psutil.AccessDenied:
                summary.append(
                    "psutil is installed, but this process does not have high enough access rights "
                    "to query process information."
                )
                summary.append("")  # blank line

        cache_summary = f"`{len(ctx.bot.guilds)}` guild(s) and `{len(ctx.bot.users)}` user(s)"

        # Show shard settings to summary
        if isinstance(ctx.bot, discord.AutoShardedClient):
            if len(ctx.bot.shards) > 20:
                summary.append(
                    f"This bot is automatically sharded ({len(ctx.bot.shards)} shards of {ctx.bot.shard_count})"
                    f" and can see {cache_summary}."
                )
            else:
                shard_ids = ", ".join(str(i) for i in ctx.bot.shards.keys())
                summary.append(
                    f"This bot is automatically sharded (Shards {shard_ids} of {ctx.bot.shard_count})"
                    f" and can see {cache_summary}."
                )
        elif ctx.bot.shard_count:
            summary.append(
                f"This bot is manually sharded (Shard {ctx.bot.shard_id} of {ctx.bot.shard_count})"
                f" and can see {cache_summary}."
            )
        else:
            summary.append(f"This bot is not sharded and can see {cache_summary}.")

        # pylint: disable=protected-access
        ctx.bot._connection.max_messages = 1000000000000000000000000000000000000000000000000000000000000000000000000000
        if ctx.bot._connection.max_messages:
            message_cache = f"Message cache capped at {ctx.bot._connection.max_messages}"
        else:
            message_cache = "Message cache is disabled"

        if discord.version_info >= (1, 5, 0):
            presence_intent = f"presence intent is {'enabled' if ctx.bot.intents.presences else 'disabled'}"
            members_intent = f"members intent is {'enabled' if ctx.bot.intents.members else 'disabled'}"

            summary.append(f"{message_cache}, {presence_intent} and {members_intent}.")
        else:
            guild_subscriptions = (
                f"guild subscriptions are {'enabled' if ctx.bot._connection.guild_subscriptions else 'disabled'}"
            )

            summary.append(f"{message_cache} and {guild_subscriptions}.")

        # pylint: enable=protected-access

        # Show websocket latency in milliseconds
        summary.append(f"Average websocket latency: {round(ctx.bot.latency * 1000, 2)}ms")

        async with ctx.bot.embed(description="\n".join(summary)) as emb:
            await emb.send(ctx.channel)

    @Feature.Command(parent="jsk", name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Direct evaluation of Python code.
        """

        arg_dict = get_var_dict_from_ctx(ctx, Flags.SCOPE_PREFIX)
        try:
            arg_dict["ref"] = ctx.message.reference.resolved
        except:
            arg_dict["ref"] = None
        arg_dict["oahx"] = ctx.bot
        arg_dict["owners"] = [await ctx.bot.try_user(id) for id in ctx.bot.owner_ids]
        arg_dict["_"] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                    async for send, result in AsyncSender(executor):
                        if result is None:
                            continue

                        self.last_result = result

                        send(await self.jsk_python_result_handling(ctx, result))

        finally:
            scope.clear_intersection(arg_dict)


def setup(bot):
    bot.add_cog(CustomDebugCog(bot=bot))
