import discord, datetime, asyncio
from discord.ext import commands

class CacheError(Exception):
    def __init__(self, message : str):
        super().__init__(message)

class CacheOutput:
    def __init__(self, cache_system, data):       
        self.cache = cache_system
        self.data = data     

    def replace(self, result_name, result_output):
        self.data[result_name] = result_output
        return self

    def insert(self, result_name, result_output):
        self.data[result_name] = result_output
        return self

    def delete(self, result_name):
        try:
            del self.data[result_name]
        except Exception:
            raise CacheError(f"{result_name} is not in the cach.")
        else:           
            return self

    def get(self, result_name):
        try:
            result = self.data[result_name]  
        except Exception:
            raise CacheError(f"{result_name} is not in the cache.")
        else:
            return result
            
class Cache:
    def __init__(self):  
        self.properties = CacheOutput(self, {})

class Processing:
    def __init__(self, ctx):
        self._start = None
        self._end = None
        self.ctx = ctx      
        
    async def __aenter__(self):
        self.message = await self.ctx.send(embed=discord.Embed(title="Processing...", description="<a:loading:747680523459231834> Processing command, please wait...", colour=self.ctx.bot.colour))
        return self
        
    async def __aexit__(self, *args, **kwargs):
        return await self.message.delete()                                 

class CustomEmbed:
    def __init__(self, *args, **kwargs):
        self.timestamp = kwargs.pop("timestamp", datetime.datetime.utcnow())
        self.title = kwargs.pop("title")
        self.description = kwargs.pop("description")
        self.footer = kwargs.pop("footer",None)  
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        embed = discord.Embed()    
        self.embed = embed.from_dict({"color": 6567423, "type": "rich", "title": self.title, "description": self.description, "footer": self.footer})
 
    async def __aexit__(self, *args, **kwargs):
        return self                                                                                                  
    async def __aenter__(self):
        return self
        
    async def send(self, channel, *args, **kwargs):
        return await channel.send(embed=self.embed, *args, **kwargs)