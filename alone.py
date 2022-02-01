import discord
from discord.ext import commands
from utils.CustomContext import CoolContext
from discord.http import HTTPClient
import asyncio
from utils.models import Client
from discord.ext.commands.view import StringView

class Alone(commands.Bot):
	def __init__(self, command_prefix, help_command=None, description=None, mount = None, **options):
		super().__init__(command_prefix, help_command, description, **options)
		self._bot : commands.Bot = mount
		
	async def get_context(self, message: discord.Message, *, cls = CoolContext):
		"""|coro|

        Returns the invocation context from the message.

        This is a more low-level counter-part for :meth:`.process_commands`
        to allow users more fine grained control over the processing.

        The returned context is not guaranteed to be a valid invocation
        context, :attr:`.Context.valid` must be checked to make sure it is.
        If the context is not valid then it is not a valid candidate to be
        invoked under :meth:`~.Bot.invoke`.

        Parameters
        -----------
        message: :class:`discord.Message`
            The message to get the invocation context from.
        cls
            The factory class that will be used to create the context.
            By default, this is :class:`.Context`. Should a custom
            class be provided, it must be similar enough to :class:`.Context`\'s
            interface.

        Returns
        --------
        :class:`.Context`
            The invocation context. The type of this can change via the
            ``cls`` parameter.
        """
		view = StringView(message.content)
		ctx = cls(prefix=None, view=view, bot=self, message=message)
		if message.author.id == 844213992955707452:  # type: ignore
			return ctx
			
		prefix = await self.get_prefix(message)
		invoked_prefix = prefix
		if isinstance(prefix, str):
			if not view.skip_string(prefix):
				return ctx
		else:
			try:
				if message.content.startswith(tuple(prefix)):
					invoked_prefix = discord.utils.find(view.skip_string, prefix)
				else:
					return ctx
					
			except TypeError:
				if not isinstance(prefix, list):
					raise TypeError(
                        "get_prefix must return either a string or a list of string, "
                        f"not {prefix.__class__.__name__}"
                    )

                # It's possible a bad command_prefix got us here.
				for value in prefix:
					if not isinstance(value, str):
						raise TypeError(
                            "Iterable command_prefix or list returned from get_prefix must "
                            f"contain only strings, not {value.__class__.__name__}"
                        )

                # Getting here shouldn't happen
				raise
			
		if self.strip_after_prefix:
			view.skip_ws()
			
		invoker = view.get_word()
		ctx.invoked_with = invoker
        # type-checker fails to narrow invoked_prefix type.
		ctx.prefix = invoked_prefix  # type: ignore
		ctx.command = self.all_commands.get(invoker)
		return ctx
		
	async def on_message(self, message : discord.Message):
		if message.content.startswith("alone "):
			ctx = await self.get_context(message, cls=CoolContext)
			try:
				return await ctx.command.callback()
			except:
				pass
		return await self.process_commands(message)