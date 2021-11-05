import discord, asyncpg, asyncio, datetime, os, time, copy, re
from discord.ext import commands

from utils.CustomContext import CoolContext
from utils.subclasses import Processing, CustomEmbed, Cache


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
        
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
        
class Oahx(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False), case_insensitive=True, *args, **kwargs)
        self.__extensions = [f"extensions.{item[:-3]}" for item in os.listdir("./extensions") if item != "help.py"]
        self.help_command = None        
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        self.maintenance = False
        self.owner_maintenance = False
        self.embed = CustomEmbed
        self.owner_ids = {746807014658801704, 733370212199694467, 797044260196319282, 668906205799907348, 631821494774923264}
        self.mods = {746807014658801704, 733370212199694467, 797044260196319282, 668906205799907348, 631821494774923264}
        self.beta_commands = []
        self.exts = set()       
        self.processing = Processing
        [self.load_extension(cog) for cog in self.__extensions if cog != "extensions.__pycach"]
        self.cache = Cache(self.loop)
        self.cache.insert("prefixes", {})
        self.bot_id = 844213992955707452
        self.mentions = [f"<@{self.bot_id}>", f"<@!{self.bot_id}>"]
        self.add_check(self.beta_command_activated) 
        
    async def on_message(self, message : discord.Message):
        if message.content.startswith("oahx "):
             ctx = await self.get_context(message)
             try:
                 await ctx.command.callback()
             except:
                 pass          
        if message.content in self.mentions:
            alt_message : discord.Message = copy.copy(message)
            alt_message.content += " prefix"
            context = await self.get_context(alt_message)
            await self.invoke(context)                      
        await self.process_commands(message)                                 
        
    async def beta_command_activated(self, ctx : CoolContext):
        if ctx.author.id in ctx.bot.mods:
            return True
        elif ctx.command.name in ctx.bot.beta_commands:
            async with ctx.bot.embed(title="Sorry.", description="This command is in the beta version of Oahx, please wait until its fully released.") as embed:
                await embed.send(ctx.channel)
                return False
        else:
            return True
        
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CoolContext)                                         
    async def on_ready(self):
		    
		    print(
        "Logged in! \n"
        f"{'-' * 20}\n"
        f"Bot Name: {self.user} \n"
        f"Bot ID: {self.user.id} \n"
        f"Bot Guilds: {len(self.guilds)} \n"
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
bot.run("ODQ0MjEzOTkyOTU1NzA3NDUy.YKPJjA.n_Ha1X5zMlz-QOCOHYx5WkEDnkc")            
