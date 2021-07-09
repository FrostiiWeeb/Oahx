import discord
from discord.ext import commands
from durations import Duration

class TimeConverter(commands.Converter):

    def __int__(self):
        return self.converted_time.to_seconds()                        
    def convert(self, time : str):
    	try:
    		self.converted_time = Duration(time)
    		
    		return converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e) from e
    	
						