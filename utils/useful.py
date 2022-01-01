import discord, re    
from discord.ext import commands
from functools import wraps
from durations import Duration as DurationConvertion
from argparse import ArgumentParser

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
    	
						