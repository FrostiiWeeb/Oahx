import discord, asyncio
from discord.ext import commands

class CacheError(Exception):
    def __init__(self, message : str):
        super().__init__(message)

class CacheOutput:
    def __init__(self, cache_system):
        self.cache = cache_system

    def replace(self, result_name, result_output):
        self.cache._properties[result_name] = result_output
        return self

    def insert(self, result_name, result_output):
        self.cache._properties[result_name] = result_output
        return self

    def delete(self, result_name):
        try:
            del self.cache._properties[result_name]
        except Exception:
            raise CacheError(f"{result_name} is not in the cach.")
        else:           
            return self

    def get(self, result_name):
        try:
            result = self.cache._properties[result_name]  
        except Exception:
            raise CacheError(f"{result_name} is not in the cache.")
        else:
            return result
            
class Cache:
    def __init__(self):
        self._properties = {}  
        self.properties = CacheOutput(self)

class CoolContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = Cache()
        
    async def fancy_send(self, text : str, speed : int = 1, *args, **kwargs):
        full_text = f"{text[0]}"                    
        message = await super().send(full_text, *args, **kwargs)        
        for letter in text[1:]:
            full_text += letter        
            await message.edit(full_text, *args, **kwargs)
            await asyncio.sleep(speed)                          