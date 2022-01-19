import discord, asyncpg, asyncio, datetime, os, time, copy, re
from discord.ext import commands

from utils.CustomContext import CoolContext
from utils.subclasses import Processing, CustomEmbed, Cache
from discord.ext import cli, ipc
import aiohttp, uvloop
from utils.useful import get_prefix
import asyncrd

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


async def run():
    bot = Oahx(command_prefix=get_prefix, intents=discord.Intents.all(), db=None)
    bot.ipc.start() 
    bot.db = await asyncpg.create_pool(
        dsn="postgres://merxmfgczboito:3e88a71de02e92ee7fb5f04d0773bb61f131f45e1dff70d0a497cdee4592a348@ec2-34-250-92-138.eu-west-1.compute.amazonaws.com:5432/dd85gkpf1k6u9b", max_queries=100000000
    )
    redis = await asyncrd.connect("redis://localhost:7000")
    bot.redis = redis
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS prefixes(guild_id bigint PRIMARY KEY, prefix TEXT)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS numbers(number TEXT PRIMARY KEY, channel_id bigint, name TEXT, id bigint)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS premium_users(code TEXT PRIMARY KEY, user_id bigint, name TEXT)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS application_setup(guild_id bigint PRIMARY KEY, channel_id bigint, skill_dm boolean)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS application(id text PRIMARY KEY, guild_id bigint, channel_id bigint, why_staff text, why_choose_you text, what_bring text, how_help text)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS tags(user_id bigint, name text PRIMARY KEY, content text, author TEXT, timestamp BIGINT)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS economy(user_id bigint PRIMARY KEY, wallet bigint, bank bigint)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS cooldown_channel(channel_id bigint, command TEXT PRIMARY KEY)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS cooldown_user(user_id bigint, command TEXT PRIMARY KEY)"
    )
    await bot.db.execute(
        "CREATE TABLE IF NOT EXISTS cooldown_guild(guild_id bigint, command TEXT PRIMARY KEY)"
    )
    try:
        await bot.start("ODQ0MjEzOTkyOTU1NzA3NDUy.YKPJjA.n_Ha1X5zMlz-QOCOHYx5WkEDnkc")
    except KeyboardInterrupt:
        await bot.db.close()
        await bot.logout()


class Oahx(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            allowed_mentions=discord.AllowedMentions(
                roles=False, users=False, replied_user=False
            ),
            case_insensitive=True,
            *args,
            **kwargs,
        )
        self.__extensions = [
            f"extensions.{item[:-3]}" for item in os.listdir("./extensions")
        ]
        self.owner_cogs = self.__extensions
        self.help_command = None
        self.db = kwargs.pop("db", None)
        os.environ["IPC_KEY"] = "oahx_ipc"
        self.ipc = ipc.Server(self, secret_key=os.environ["IPC_KEY"], multicast_port=28900, port=7870) 
        self.client = ipc.Client(port=7870, multicast_port=28900, secret_key=os.environ.get("IPC_KEY"))
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        self.maintenance = False
        self.owner_maintenance = False
        self.embed = CustomEmbed
        self.owner_ids = {
            746807014658801704,
            733370212199694467,
            797044260196319282,
            668906205799907348,
            631821494774923264,
            699839134709317642,
        }
        self.mods = {
            746807014658801704,
            733370212199694467,
            797044260196319282,
            668906205799907348,
            631821494774923264,
            699839134709317642,
            747737674952999024,
        }
        self.beta_commands = []
        self.exts = set()
        self.processing = Processing
        [
            self.load_extension(cog)
            for cog in self.__extensions
            if cog != "extensions.__pycach"
        ]
        self.cache = Cache(self.loop)
        self.cache.insert("prefixes", {})
        self.bot_id = 844213992955707452
        self.mentions = [f"<@{self.bot_id}>", f"<@!{self.bot_id}>"]
        self.colour, self.color = discord.Colour.from_rgb(
            100, 53, 255
        ), discord.Colour.from_rgb(100, 53, 255)
        self.emoji_dict = {
            "greyTick": "<:greyTick:596576672900186113>",
            "greenTick": "<:greenTick:820316551340490752>",
            "redTick": "<:redTick:820319748561829949>",
            "dpy": "<:dpy:596577034537402378>",
            "py": "<:python:286529073445076992>",
            "coin": "<:emoji_4:904048735762395176>",
        }
        self.add_check(self.beta_command_activated)

    async def try_channel(self, channel_id: int):
        channel = super().get_channel(channel_id)
        if not channel:
            channel = await super().fetch_channel(channel_id)
        return channel

    async def try_user(self, user_id: int):
        user = super().get_user(user_id)
        if not user:
            channel = await super().fetch_user(user_id)
        return user

    async def on_message(self, message: discord.Message):
        if message.content.startswith("oahx "):
            ctx = await self.get_context(message)
            try:
                await ctx.command.callback()
            except:
                pass
        if message.content in self.mentions:
            alt_message: discord.Message = copy.copy(message)
            alt_message.content += " prefix"
            context = await self.get_context(alt_message)
            await self.invoke(context)
        await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        if before.content.lower() == after.content.lower():
            return
        if after.attachments:
            return
        await self.process_commands(after)

    async def beta_command_activated(self, ctx: CoolContext):
        if ctx.author.id in ctx.bot.mods:
            return True
        elif ctx.command.name in ctx.bot.beta_commands:
            async with ctx.bot.embed(
                title="Sorry.",
                description="This command is in the beta version of Oahx, please wait until its fully released.",
            ) as embed:
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


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.new_event_loop()
asyncio.ensure_future(run(), loop=loop)
loop.run_forever()
