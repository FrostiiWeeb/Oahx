import discord, re
from discord.ext import commands

TIME_OBJECT = {'seconds': 1, 's': 1, 'minutes': 60, "m": 60, 'hours': 3600, 'hour': 3600, 'h': 3600, "day": 86400, "days": 86400, "d": 86400, "year": 31536000, "years": 31536000, "y": 31536000}

class Duration:
    def __init__(self, time : str):
        self.time = time
                                           
    def seperate(self, string, seperator):
        data = sting.split(seperator)
        return data
                                                   
    def convert(self):
        if "and" in self.time:
            time_real = self.seperate(self.time, "and")
        elif "," in self.time:
            time_real = self.seperate(self.time, ",")   
        end_time = 0                                
        for time in time_real:
            integer_real = re.search("\\d+", time).group(0)
            time_for_real = time.strip(str(integer_real))
            convert_time_to = time_for_real
            convert_to = TIME_OBJECT[convert_time_to]
            calc_time = integer_real * convert_to
            end_time += calc_time
        return end_time
        
class TimeConverter(commands.Converter):

    def __int__(self):
        return self.converted_time
                                
    async def convert(self, ctx, time : str):
    	try:
    	    self.converted_time = Duration(time)
    	    self.converted_time = self.converted_time.convert()
    	    return self.converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e) from e
    	
						