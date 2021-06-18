import discord
from discord.ext import commands
import asyncpg, asyncio
import discord
from discord.ext import commands
import datetime
import asyncio
import os
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

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

async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("oahx ")(bot, message)
    try:
        prefix = await bot.db.fetch("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)   
        prefix = prefix['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    except Exception:
        return commands.when_mentioned_or("oahx ")(bot, message)
        
class Oahx(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False), case_insensitive=True, *args, **kwargs)
        self.__extensions = [f"extensions.{item[:-3]}" for item in os.listdir("./extensions") if item != "__pycache__"] + ["jishaku"]
        [self.load_extension(cog) for cog in self.__extensions if cog != "__pycache__"]
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        self.embed = CustomEmbed
        self.languages = {"french": {"someone": "quelque-un"}}
                          
    async def on_ready(self):
		    
		    print(
        "Logged in! \n"
        f"{'-' * 20}\n"
        f"Bot Name: {self.user} \n"
        f"Bot ID: {self.user.id} \n"
        f"Bot Guilds: {self.guilds} \n"
        f"{'-' * 20}"
    )

async def run(bot):
    bot.db = await asyncpg.create_pool("postgres://jmwizyznmjwjjv:9c8ccd9ab90e06bb398c4a6e897951e6ff401beb3d8f8f24f82658064551c8fb@ec2-52-7-168-69.compute-1.amazonaws.com:5432/d4vp6kug2vm5t2")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes(guild_id bigint PRIMARY KEY, prefix TEXT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS numbers(number TEXT PRIMARY KEY, channel_id bigint, name TEXT)")

bot = Oahx(command_prefix=get_prefix, intents=discord.Intents.all())
loop = asyncio.get_event_loop()
loop.run_until_complete(run(bot=bot))
bot.run("ODQ0MjEzOTkyOTU1NzA3NDUy.YKPJjA.zlx8JnZ3D8sftVBTXk8YwG88--I")            
