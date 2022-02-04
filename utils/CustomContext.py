import discord, asyncio
from discord.ext import commands
import aiohttp
from .models import Confirmation


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
