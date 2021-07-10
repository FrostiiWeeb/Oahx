import discord
from discord.ext import commands

TIME_OBJECT = {'seconds': 1, 's': 1, 'minutes': 60, "m": 60, 'hours': 3600, 'hour': 3600, 'h': 3600, "day": 86400, "days": 86400, "d": 86400, "year": 31536000, "years": 31536000, "y": 31536000}

class Duration:
    def __init__(self, time : str):
        self.time = time
               
    def convert(self, time_thing : str):
        time_sep = time_thing.split("and")
        end_time = 0
        for time in time_sep:
            if time.endswith("h") or time.endswith("s") or time.endswith("m") or time.endswith("d") or time.endswith("y"):
                real = ""
                sep = ""
                for time_lol in time:
                    try:
                        real_ = int(time_lol)
                        real += str(real_)
                    except:
                        sep += time_lol
                real = int(real)
                sep = int(TIME_OBJECT[sep])
                return real * sep                 
            real_time = time.split(" ")
            first = real_time[0]
            if first == "few":
                first = 3
            first = int(first)
            second = real_time[1]
            second = TIME_OBJECT[second]
            calc_time = first * second
            end_time += calc_time
        return end_time
                               

class TimeConverter(commands.Converter):

    def __int__(self):
        return self.converted_time
                                
    async def convert(self, ctx, time : str):
    	try:
    	    self.converted_time = Duration(time)
    	    self.converted_time = self.converted_time.convert(time)
    	    return self.converted_time
    		
    	except Exception as e:
    		print(e)
    		raise Exception(e) from e
    	
						