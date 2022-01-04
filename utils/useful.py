import discord, re    
from discord.ext import commands
from functools import wraps
from durations import Duration as DurationConvertion
from argparse import ArgumentParser

async def get_prefix(bot, message):
    try:
        ctx = message
        if ctx.author.id in bot.owner_ids or ctx.author.id in bot.mods:
            return commands.when_mentioned_or(*["oahx ", "boahx "])(bot, message)
        prefix_cache = bot.cache.get("prefixes")
        if str(ctx.guild.id) in prefix_cache:
            return commands.when_mentioned_or(prefix_cache[str(ctx.guild.id)])(bot, message)
        prefix = await bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
        return commands.when_mentioned_or(prefix['prefix'])(bot, message)
    except Exception:
        ctx = message
        prefix_cache = bot.cache.get("prefixes")
        prefix_cache[str(ctx.guild.id)] = "oahx "
        return commands.when_mentioned_or("oahx ")(bot, message) 

class FlagParser(ArgumentParser):
    def __init__(self, bot : commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.args = []
        
    async def load_error(self, ctx : commands.Context, name : str):
        help = None
        for n, v in self.args:
            if n == name:
                help = v 
        return await ctx.send(help)         
        
    def add_command_argument(self, name : str, help : str):
        self.args.append((name, help))
        self.add_argument(name, help=help)                           
          

            
class Duration:
    def __init__(self, time : str):
        self.time = time                                          
                                                   
    def convert(self):
        return DurationConvertion(self.time)                
        
class TimeConverter(commands.Converter):

    def __int__(self):
        pass
                                
    async def convert(self, ctx, time : str):
    	try:
    	    self.converted_time = Duration(time=time)
    	    self.converted_time = self.converted_time.convert()
    	    return self.converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e) from e
    	
						