import discord, asyncio
from discord.ext import commands
import aiohttp
from .models import Confirmation
from typing import *
import copy

class CoolContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)       
        self._bot : commands.Bot = self.bot       

    async def prompt(self, description : str, embed : bool = True):
        if embed:
            async with self.bot._bot.embed(description=description) as emb:
                view = Confirmation(self)
                await emb.send(self.channel, view=view)
                await view.wait()
                return view.value
        view = Confirmation(self)
        await self.send(description, view=view)
        await view.wait()
        return view.value

    async def exec_as(self, user : Union[discord.User, discord.Member, int], command : commands.Command = None, bypass : bool = False):
        copy_context = copy.copy(self)
        copy_context.author = user
        copy_context.command = command or self.command
        return await self._bot.invoke(copy_context) if not bypass else await copy_context.reinvoke()

    async def bypass(self, user : Union[discord.User, discord.Member, int] = None, *args, **kwargs):
        return await self.exec_as(user=user or self.author, bypass=True, *args, **kwargs)

    async def fancy_send(self, text: str, speed: int = 1, *args, **kwargs):
        full_text = f"{text[0]}"
        await asyncio.sleep(0.5)
        message = await super().send(full_text, *args, **kwargs)
        for letter in text[1:]:
            full_text += letter
            await asyncio.sleep(speed)
            await message.edit(full_text, *args, **kwargs)


    async def send(self, content : str = None, embed : discord.Embed = None, file : discord.File = None, files : List[discord.File] = None, view : discord.ui.View = None, delete_after : int = None, reply_to : discord.Message = None, *args, **kwargs):
        if embed:
            embed.colour = self.bot.colour
            embed.set_footer(text="Requested by {.author}".format(self), icon_url=self.author.avatar.url)
        if self.bot.http.token in content:
            if embed:
                if self.bot.http.token in embed.title or self.bot.http.token in embed.description:
                    embed.title = embed.title.replace(self.bot.http.token, "[token omitted]")
                    embed.description = embed.title.replace(self.bot.http.token, "[token omitted]")
            content = content.replace(self.bot.http.token, "[token omitted]")
        return await super().send(content, embed=embed, file=file, files=files, delete_after=delete_after, reference=reply_to, mention_author=False, view=view, *args, **kwargs)