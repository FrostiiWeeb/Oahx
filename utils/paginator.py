import discord
from discord.ext import commands
import asyncio
import typing

#


class PaginatorButton(discord.ui.View):
    def __init__(self, text: str = None, pages: typing.List[discord.Embed] = None):
        super().__init__()
        self.value = None
        self.pages = pages
        self.text = text
        self.total_pages = len(self.pages)

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(style=discord.ButtonStyle.green, emoji="<:oahx_left:859143802005356615>")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(style=discord.ButtonStyle.grey, emoji="<:oahx_stop:859143862089023528>")
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class PaginationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class OahxEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(colour=discord.Colour.from_rgb(100, 53, 255), **kwargs)


class OahxPaginator:
    __slots__ = (
        "pages",
        "text",
        "buttons",
        "message",
        "total_pages",
        "current_page",
        "use_custom_embed",
        "use_default_embed",
        "page_embed",
        "message",
        "title",
        "description",
        "timestamp",
        "colour",
        "color",
        "timeout",
    )

    def __init__(
        self,
        pages=None,
        text=None,
        title=None,
        description=None,
        timestamp=None,
        colour=discord.Colour.blurple(),
        color=discord.Colour.blurple(),
        timeout: int = 60,
    ):
        self.pages = pages
        self.text = text
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.timeout = timeout
        self.colour = colour
        self.color = color
        self.buttons = [
            "<:oahx_left:859143802005356615>",
            "<:oahx_right:859143734921527316>",
            "<:oahx_stop:859143862089023528>",
        ]

    async def paginate(self, ctx):
        if self.pages and self.text:
            raise RuntimeError("Connot have pages and text set at the same time.")
        if self.pages and self.text == None:
            self.total_pages = len(self.pages)
            self.current_page = 1
            self.message = await ctx.send(
                embed=self.pages[self.current_page - 1],
                view=PaginatorButton(text=self.text, pages=self.pages),
            )
            while True:
                try:
                    reaction, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda r, u: u == ctx.author and u != ctx.bot.user and not u.bot,
                        timeout=30.0,
                    )
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long to respond.")
                if str(reaction.emoji.name) == "oahx_stop":
                    await self.message.delete()
                    break
                    return
                elif str(reaction.emoji.name) == "oahx_left":
                    if self.current_page - 1 == 0:
                        pass
                    else:
                        self.current_page -= 1
                        await self.message.edit(embed=self.pages[self.current_page - 1])
                elif str(reaction.emoji.name) == "oahx_right":
                    if self.current_page - 1 == self.total_pages - 1:
                        pass
                    else:
                        self.current_page += 1
                        await self.message.edit(embed=self.pages[self.current_page - 1])
        elif self.text and self.pages == None:
            text_wrapped = [
                discord.Embed(
                    title=self.title or "Paginator",
                    description=self.text[i : i + 2000],
                    colour=self.colour or color,
                    timestamp=self.timestamp,
                )
                for i in range(0, len(self.text), 2000)
            ]
            self.total_pages = len(text_wrapped)
            self.current_page = 1
            self.message = await ctx.send(embed=text_wrapped[self.current_page - 1])
            for reaction in self.buttons:
                await self.message.add_reaction(reaction)
            while True:
                try:
                    reaction, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda r, u: u == ctx.author and u != ctx.bot.user and not u.bot,
                        timeout=30.0,
                    )
                except asyncio.TimeoutError:
                    async with ctx.bot.embed(title="Error", description="You took too long to respond.") as emb:
                        await emb.send(ctx.channel)
                        break
                if str(reaction.emoji.name) == "oahx_stop":
                    await self.message.delete()
                    break
                    return
                elif str(reaction.emoji.name) == "oahx_left":
                    if self.current_page - 1 == 0:
                        pass
                    else:
                        self.current_page -= 1
                        await self.message.edit(embed=text_wrapped[self.current_page - 1])
                elif str(reaction.emoji.name) == "oahx_right":
                    if self.current_page - 1 == self.total_pages - 1:
                        pass
                    else:
                        self.current_page += 1
                        await self.message.edit(embed=text_wrapped[self.current_page - 1])
