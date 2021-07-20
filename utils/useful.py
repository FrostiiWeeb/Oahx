import discord, re
from discord.ext import commands
from functools import wraps
from durations import Duration as DurationConvertion

class Extension(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot      
        
    def load_commands(self):
        self.bot.exts.add(self)
        for command in self.cog.get_commands():
            command.cog = self
            self.bot.add_command(command)

    @property                 
    def owner(self):
        return [owner_id for owner_id in self.bot.owner_ids]
        
    def forbid_command(self, name : str):
         self.bot.beta_commands.append(name)
         
class Loader:
        
    def load(self, extension : Extension):
        extension.bot.exts.add(extension)
        return extension.load_commands()                                                                                        
class Duration:
    def __init__(self, time : str):
        self.time = time                                          
                                                   
    def convert(self):
        return DurationConvertion(self.time)                
        
class TimeConverter(commands.Converter):

    def __int__(self):
        return self.converted_time
                                
    async def convert(self, ctx, time : str):
    	try:
    	    self.converted_time = Duration(time=time)
    	    self.converted_time = self.converted_time.convert()
    	    return self.converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e) from e
    	
						