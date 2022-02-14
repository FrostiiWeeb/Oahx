import discord, asyncio
from discord.ext import commands
import aiohttp
from .models import Confirmation
from typing import *

class CoolContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)              

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
        

    async def fancy_send(self, text: str, speed: int = 1, *args, **kwargs):
        full_text = f"{text[0]}"
        await asyncio.sleep(0.5)
        message = await super().send(full_text, *args, **kwargs)
        for letter in text[1:]:
            full_text += letter
            await asyncio.sleep(speed)
            await message.edit(full_text, *args, **kwargs)


    async def send(self, content : str = None, embed : discord.Embed = None, file : discord.File = None, files : List[discord.File] = None, view : discord.ui.View = None, delete_after : int = None, reply_to : discord.Message = None):
        if embed:
            embed.colour = self.bot.colour
            embed.set_footer(text="Requested by {.author}".format(self), icon_url=self.author.avatar.url)
        return await super().send(content, embed=embed, file=file, files=file, delete_after=delete_after, reference=reply_to, mention_author=False)