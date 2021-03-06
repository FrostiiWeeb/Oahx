import discord, re
from discord.ext import commands
from functools import wraps
from durations import Duration as DurationConvertion
from argparse import ArgumentParser
import threading, typing, asyncio
from datetime import datetime


class Task:
    def __init__(self, id: int) -> None:
        self.id = id

    def stop(self):
        self.stopped = True


class Loop:
    def __init__(self, callback: typing.Callable, name: str, timeout: int) -> None:
        self.callback: typing.Callable = callback
        self.name = name
        self.timeout = timeout
        self.stopped = False


class tasks:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.loops = set()
        self.ab_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.running_tasks: typing.Set[Task] = set()
        self.current_task_id: int = 0

    async def wait_run(self, loop: Loop, coro, executor: bool = False):
        if loop.stopped:
            return
        if executor:
            time = datetime.utcnow() + __import__("datetime").timedelta(seconds=loop.timeout)
            await self.ab_loop.run_in_executor(None, coro)
            self.current_task_id += 1
            self.running_tasks.add(Task(id=self.current_task_id))
            await discord.utils.sleep_until(time)
            await self.wait_run(loop, coro, executor=executor)
        else:
            time = datetime.utcnow() + __import__("datetime").timedelta(seconds=loop.timeout)
            await coro()
            self.current_task_id += 1
            self.running_tasks.add(Task(id=self.current_task_id))
            await discord.utils.sleep_until(time)
            await self.wait_run(loop, coro, executor=executor)

    def stop_loop(self, name: str):
        for l in self.loops:
            l: Loop = l
            if l.name == name:
                l.stopped = True

    async def start_loop(self, name: str, executor: bool = False):
        for l in self.loops:
            l: Loop = l
            if l.name == name:
                if executor:
                    await self.wait_run(l, l.callback, executor=True)

                else:
                    await self.wait_run(l, l.callback, executor=False)

    def run_loop(self, *args, **kwargs):
        self.ab_loop.create_task(self.start_loop(*args, **kwargs))

    def loop(
        self,
        seconds: int = None,
        minutes: int = None,
        hours: int = None,
        days: int = None,
        name: str = None,
    ):
        cls = self
        converter = TimeConverter()
        time = 0
        if seconds:
            _time = converter.convert(", {} seconds".format(seconds))
            time += _time.to_seconds()
        if minutes:
            _time = converter.convert(", {} minutes".format(minutes))
            time += _time.to_seconds()
        if hours:
            _time = converter.convert(", {} hours".format(hours))
            time += _time.to_seconds()
        if days:
            _time = converter.convert(", {} hours".format(days))
            time += _time.to_seconds()

        def wrapper(func: typing.Callable) -> typing.Callable:
            self.loops.add(Loop(func, name or func.__name__, timeout=time))

        return wrapper


import pomice


class Queue(asyncio.Queue):
    def __init__(self, player: pomice.Player, playlist: pomice.Playlist) -> None:
        super().__init__(loop=asyncio.get_running_loop())
        self.playlist: pomice.Player = playlist
        self.player = player
        self.tracks = [track for track in self.playlist]
        self.current_track = next(self.tracks)

    async def next(self):
        await self.player.play(track=self.current_track)


class Player(pomice.Player):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queue: Queue = None

    async def next(self):
        return await self.queue.next()


async def get_prefix(bot, message):
    try:
        ctx = message
        if ctx.author.id in bot.owner_ids or ctx.author.id in bot.mods:
            return commands.when_mentioned_or(*["oahx ", "boahx ", ""])(bot, message)
        prefix = await bot.redis.hget("prefixes", message.guild.name)
        if not prefix:
            await bot.redis.hset("prefixes", message.guild.name, "oahx ")
        prefix = await bot.redis.hget("prefixes", message.guild.name)
        return commands.when_mentioned_or(prefix)(bot, message)
    except Exception:
        ctx = message
        return commands.when_mentioned_or("oahx ")(bot, message)


class FlagParser(ArgumentParser):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.args = []

    async def load_error(self, ctx: commands.Context, name: str):
        help = None
        for n, v in self.args:
            if n == name:
                help = v
        return await ctx.send(help)

    def add_command_argument(self, name: str, help: str):
        self.args.append((name, help))
        self.add_argument(name, help=help)


class Duration:
    def __init__(self, time: str):
        self.time = time

    def convert(self):
        return DurationConvertion(self.time)


class TimeConverter:
    def __int__(self):
        pass

    def convert(self, time: str):
        try:
            self.converted_time = Duration(time=time)
            self.converted_time = self.converted_time.convert()
            return self.converted_time

        except Exception as e:
            print(e)
            raise Exception(e) from e
