import discord
from discord.ext import commands
import asyncpg, asyncio
import discord
from discord.ext import commands
import datetime
import asyncio
from utils.CustomContext import CoolContext
import os, time
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

class Processing:
    def __init__(self, ctx):
        self._start = None
        self._end = None
        self.ctx = ctx      
        
    async def __aenter__(self):
        self.message = await self.ctx.send(embed=discord.Embed(title="Processing...", description="<a:loading:747680523459231834> Processing command, please wait...", colour=self.ctx.bot.colour))
        return self
        
    async def __aexit__(self, *args, **kwargs):
        await self.message.delete()
        return self                                       

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
    if message.author.id in bot.mods:
        return ['oahx ', 'boahx ']
    if not message.guild:
        return commands.when_mentioned_or("oahx ")(bot, message)
    try:
        prefix = await bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)   
        prefix = prefix['prefix']
        return commands.when_mentioned_or(prefix)(bot, message)
    except Exception:
        return commands.when_mentioned_or("oahx ")(bot, message)
        
class Oahx(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False), case_insensitive=True, *args, **kwargs)
        self.__extensions = [f"extensions.{item[:-3]}" for item in os.listdir("./Alex/Oahx/extensions") if item != "__pycache__"] + ["jishaku"]
        [self.load_extension(cog) for cog in self.__extensions if cog != "__pycache__"]
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        self.maintenance = False
        self.owner_maintenance = False
        self.embed = CustomEmbed
        self.owner_ids = {797044260196319282, 746807014658801704}
        self.mods = {797044260196319282, 746807014658801704}
        self.beta_commands = ["help"]
        self.processing = Processing
        self.languages = {"french": {"someone": "quelque-un", "hi": "bonjour", "how are you": "tu vas bien", "?": "?", ",": ","}}
        
    async def beta_command_activated(self, ctx):
        if ctx.author.id in ctx.bot.mods:
            return True
        elif ctx.command.name in ctx.bot.beta_commands:
            async with ctx.bot.embed(title="Sorry.", description="This command is in the beta version of Oahx, please wait until its fully released.") as embed:
                await embed.send(ctx.channel)
                return False
        return False
        
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CoolContext)                                         
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
    bot.beta_db = await asyncpg.create_pool("postgres://xxhhlapgszttrj:10096a300ff61f58f7b6d85c32d7de075be761a5380731c15dedfae788fc9bd5@ec2-108-128-104-50.eu-west-1.compute.amazonaws.com:5432/dr9vebh5nv6tp")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes(guild_id bigint PRIMARY KEY, prefix TEXT)")
    await bot.beta_db.execute("CREATE TABLE IF NOT EXISTS numbers(number TEXT PRIMARY KEY, channel_id bigint, name TEXT)")    
    await bot.db.execute("CREATE TABLE IF NOT EXISTS numbers(number TEXT PRIMARY KEY, channel_id bigint, name TEXT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS premium_users(code TEXT PRIMARY KEY, user_id bigint, name TEXT)")
bot = Oahx(command_prefix=get_prefix, intents=discord.Intents.all())
loop = asyncio.get_event_loop()
loop.run_until_complete(run(bot=bot))
bot.run("ODQ0MjEzOTkyOTU1NzA3NDUy.YKPJjA.3ve4a3aC8H7l_2F5FgIndydGcr4")            
