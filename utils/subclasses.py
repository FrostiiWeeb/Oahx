import discord, datetime, asyncio, humanize, sys
from discord.ext import commands

class CacheError(Exception):
    def __init__(self, message : str):
        super().__init__(message)

class CacheOutput:
    def __init__(self, cache_system):       
        self.cache = cache_system 

    @property                
    def size(self):
        return humanize.naturalsize(sys.getsizeof(self))
        
    def replace(self, result_name, result_output):
        self[result_name] = result_output
        return self

    def insert(self, result_name, result_output, delete_after=None):
        if delete_after:
            self[result_name] = result_output
            self.loop.create_task(asyncio.sleep(delete_after))
            del self[result_name]
            return self
        else:
            self[result_name] = result_output
            return self            

    def delete(self, result_name):
        try:
            del self[result_name]
        except Exception:
            raise CacheError(f"{result_name} is not in the cache.")
        else:           
            return self

    def get(self, result_name):
        try:
            result = self.cache[result_name]  
        except Exception:
            raise CacheError(f"{result_name} is not in the cache.")
        else:
            return result
            
class Cache(dict, CacheOutput):
    def __init__(self, loop, *args, **kwargs):        
        super().__init__(*args, **kwargs)  
        self.loop = loop      

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

#class Extension:
#    def __init__(self, bot, name : str = None):
#        self.bot = bot
#        self.commands = {command for command in dir(self) if not command.startswith('__')}     
#        self.name = name or self.__class__.__name__
#        for command in self.commands:
#            func = getattr(self, command)
#            self.bot.add_command(commands.Command(name=func.__name__, description=func.__doc__, func=func))        

class CustomEmbed:
    def __init__(self, *args, **kwargs):
        self.timestamp = kwargs.pop("timestamp", datetime.datetime.utcnow())
        self.title = kwargs.pop("title")
        self.description = kwargs.pop("description")
        self.footer = kwargs.pop("footer",None)  
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        embed = discord.Embed()    
        self.embed = embed.from_dict({"color": 6567423, "type": "rich", "title": self.title, "description": self.description, "footer": self.footer or "Oahx is property of AlePI"})
 
    async def __aexit__(self, *args, **kwargs):
        return self                                                                                                  
    async def __aenter__(self):
        return self
        
    async def send(self, channel, *args, **kwargs):
        return await channel.send(embed=self.embed, *args, **kwargs)