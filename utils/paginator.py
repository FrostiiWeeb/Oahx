import discord
from discord.ext import commands

# [result[i : i + 2000] for i in range(0, len(result), 2000)]

class PaginationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class OahxPaginatorEmbed:
    def __init__(self, embed : discord.Embed):
        self.embed = embed
        self.title = embed.title
        self.description = embed.description
        self.footer = embed.footer
        self.timestamp = embed.timestamp
        self.thumbnail = embed.thumbnail
        self.author = embed.author  
        self.icon_url = embed.icon_url                                     
class OahxPaginator:
    __slosts__ = ('pages', 'text', 'buttons', 'message', 'total_pages', 'current_page', 'use_custom_embed', 'use_default_embed', 'page_embed', 'message')
    def __init__(self, pages=None, text=None):
        self.pages = pages
        self.text = text
        self.buttons = [("<:oahx_left:859143802005356615>"), ("<:oahx_right:859143734921527316>"), ("<:oahx_stop:859143862089023528>")]
        
        async def paginate(self, ctx):
            if self.pages and self.text:
                raise RuntimeError("Connot have pages and text set at the same time.")
            if self.pages and self.text == None:
                self.total_pages = len(self.pages)-1
                self.current_page = 1
                self.message = await ctx.send(embed=self.pages[self.current_page-1])
                for reaction in self.buttons:
                    await self.message.add_reaction(reaction)
                while True:
                    reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda r,u: u == ctx.author and u != bot.user and not u.bot)
                    if str(reaction.emoji.name) == "oahx_stop":
                        async with ctx.bot.processing(ctx):
                            await asyncio.sleep(3)
                            await self.message.delete()
                            break
                            return
                    if str(reaction.emoji.name) == "oahx_left":
                        async with ctx.bot.processing(ctx):
                            await asyncio.sleep(3)
                            if self.current_page-1 == 0:
                                raise PaginationError("Maxed-out pages.")
                            else:
                                self.current_page -= 1
                                await self.message.edit(embed=self.pages[self.current_page-1])
                    if str(reaction.emoji.name) == "oahx_right":
                        async with ctx.bot.processing(ctx):
                            await asyncio.sleep(3)
                            if self.current_page-1 == len(self.total_pages):
                                raise PaginationError("Maxed-out pages.")
                            else:
                                self.current_page += 1
                                await self.message.edit(embed=self.pages[self.current_page-1])                                                                
                                                                                                                    