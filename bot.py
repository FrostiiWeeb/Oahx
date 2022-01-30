
import discord, asyncpg, asyncio, datetime, os, time, copy, re
from discord.ext import commands

from utils.CustomContext import CoolContext
from utils.subclasses import Processing, CustomEmbed, Cache
from discord.ext import cli, ipc
import aiohttp, uvloop
from utils.useful import get_prefix
from utils import tasks
import asyncrd
import topgg
import slash_util
import databases
import orm
import sqlalchemy
import asyncio
import pomice
from utils.mounting import Mount

database = databases.Database("postgresql://frostiiweeb:my_password@localhost/oahx")
metadata = orm.ModelRegistry(database=database)

class Prefixes(orm.Model):
    tablename = "prefixes"
    registry = metadata

    fields = {"guild_id": orm.BigInteger(primary_key=True), "prefix": orm.Text()}


class Snipes(orm.Model):
    tablename = "snipes"
    registry = metadata

    fields = {
        "message_id": orm.BigInteger(primary_key=True),
        "content": orm.String(max_length=2000),
    }


class EditSnipes(orm.Model):
    tablename = "editsnipes"
    registry = metadata

    fields = {
        "message_id": orm.BigInteger(primary_key=True),
        "before_content": orm.String(max_length=2000),
        "after_content": orm.String(max_length=2000),
    }

class WhichBot(orm.Model):
    tablename = "whichbot"
    registry = metadata

    fields = {
        "user_id": orm.BigInteger(primary_key=True),
        "bot": orm.Integer()
    }


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


class Alone(commands.Bot):
    def __init__(self, command_prefix, help_command=commands.DefaultHelpCommand(), description=None, **options):
        super().__init__(command_prefix, help_command, description, **options)

    async def on_message(self, message):
        if message.author.id == 412734157819609090:
            if message.content == "alone help":
                return await message.channel.send("Hello! I am ALone Bot. I was mounted on Oahx by FrostiiWeeb.")

subbot = Alone(command_prefix="alone ", intents=discord.Intents.all())

async def run():
    bot = Oahx(command_prefix=get_prefix, intents=discord.Intents.all(), db=None)
    bot.ipc.start()
    import orm
    await metadata.create_all()
    bot.prefixes = Prefixes
    bot.snipes = Snipes
    bot.editsnipes = EditSnipes
    bot.whichbot = WhichBot
    bot.orm = database
    bot.meta_orm = metadata
    bot.mounter.mount(subbot)
    @bot.command()
    async def switch(ctx, bot : str):
        bots = ["oahx", "alone"]
        if bot == bots[0]:
            await bot.whichbot.objects.create(user_id=ctx.author.id, bot=1)
        elif bot == bots[1]:
            await bot.whichbot.objects.create(user_id=ctx.author.id, bot=2)
        return await ctx.send(f"You have now switched to {bot}.")

    bot.db = await asyncpg.create_pool(
        dsn="postgresql://frostiiweeb:my_password@localhost/oahx", max_queries=100000000
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
        import wavelink
        self.__users = {}
        self.mounter = Mount(self)
        self.wavelink = wavelink.NodePool()
        self.pomice = pomice.NodePool()
        self.__extensions = [
            f"extensions.{item[:-3]}" for item in os.listdir("./extensions")
        ]
        self.owner_cogs = self.__extensions
        self.help_command = None
        self.db = kwargs.pop("db", None)
        os.environ["IPC_KEY"] = "oahx_ipc"
        self.ipc = ipc.Server(self, secret_key="oahx_ipc", port=7870)
        self.client = ipc.Client(secret_key="oahx_ipc", port=7870)
        self.colour = discord.Colour.from_rgb(100, 53, 255)
        self.maintenance = False
        self.owner_maintenance = False
        self.mounter = Mount(self)
        self.tasks = tasks()
        self.embed = CustomEmbed
        self.pomice = pomice.NodePool()
        self.owner_ids = {
            746807014658801704,
            733370212199694467,
            797044260196319282,
            668906205799907348,
            631821494774923264,
            699839134709317642,
            744316348078751914,
            412734157819609090,
        }
        self.mods = {
            746807014658801704,
            733370212199694467,
            797044260196319282,
            668906205799907348,
            631821494774923264,
            699839134709317642,
            747737674952999024,
            744316348078751914,
            412734157819609090,
        }
        self.beta_commands = []
        self.exts = set()
        self.mounts = {}
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

    async def try_guild(self, guild_id: int):
        guild = super().get_guild(guild_id)
        if not guild:
            guild = await super().fetch_guild(guild_id)
        return guild

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

    async def on_message(self, message : discord.Message):
        ctx = message
        whichbot = await self.db.fetchrow("SELECT * FROM whichbot WHERE user_id = $1", ctx.author.id)
        if not whichbot:
            whichbot = {"bot": 1}
        if whichbot["bot"] == 1:
            if message.content.startswith("oahx "):
                ctx = await self.get_context(message)
                try:
                    return await ctx.command.callback()
                except:
                    pass
                if message.content in self.mentions:
                    alt_message: discord.Message = copy.copy(message)
                    alt_message.content += " prefix"
                    context = await self.get_context(alt_message)
                    return await self.invoke(context)
                return await self.process_commands(message)
        return await self.mounts[int(whichbot["bot"])].on_message(message=message)

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
        self.session = aiohttp.ClientSession(loop=self.loop)
        await self.cogs["Music"].start_nodes()
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
#
# @tasks.loop(seconds=60)
# async def update_stats()
loop.run_forever()
