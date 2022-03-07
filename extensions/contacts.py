import discord, io
from discord.ext import commands
from difflib import get_close_matches
import random
import traceback
import asyncio
from discord.ext.commands.cooldowns import BucketType
from typing import Union, List
import datetime

from extensions.economy import NotInDB


class Call:
    def __init__(
        self,
        channel: discord.TextChannel,
        recipients: List[Union[discord.User, discord.Member]],
    ):
        self.channel = channel
        self.recipients = recipients

    def raise_error(self, *args, **kwargs):
        raise ConnectionError("The call was ended, aborting...")

    async def close(self, ctx):
        await self.channel.send("Call ended")
        await ctx.send("Call ended")
        self.channel = None
        self.recipients = None
        self.respond = self.raise_error

    async def respond(self, ctx, user: str = "me", message: str = None, *args, **kwargs):
        if not (self.channel, self.recipients):
            raise Exception("The call was ended, aborting...")
        if user == "me":
            await ctx.send(f"{self.recipients[1]}: {message}", *args, **kwargs)
        else:
            await self.channel.send(f"{self.recipients[0]}: {message}", *args, **kwargs)


class PhoneEmbed(discord.Embed):
    def __init__(self, description, **kwargs):
        super().__init__(
            color=discord.Color.from_rgb(100, 53, 255),
            title="Phone Error",
            description=description,
            timestamp=datetime.datetime.utcnow(),
        )


class NumberNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)


class InDB(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConnectionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Contacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mutes = {}
        self.calls = {}

    async def try_channel(self, channel):
        channel_data = self.bot.get_channel(channel)
        if channel_data is None:
            channel_data = await self.bot.fetch_channel(channel)
        return channel_data

    async def call_support(self, ctx, channel):
        if channel:
            channel = await self.try_channel(854670283457429524)
            await channel.send(
                "<@&854668670168858624> <@&854669288572059669> <@&854669613442662411> Hey, theres someone asking for help!"
            )
            await ctx.send("Hello! Welcome to Customer Support, how may we help you?")

            def check(m):
                return (
                    m.author.name == ctx.author.name
                    or m.channel.id == 854670283457429524
                    and m.author.name != ctx.author.name
                )

            while True:
                message = await self.bot.wait_for("message", check=check)
                if message.content == f"{ctx.prefix}hangup":
                    self.using_support = False
                    await ctx.send("Call ended")
                    await channel.send("Call ended")
                    return
                elif message.author.name == ctx.author.name and message.channel.id != 854670283457429524:
                    await channel.send(f"{ctx.author.name}: {message.content}")
                elif message.channel.id == 854670283457429524:
                    await ctx.send(f"Support Team: {message.content}")

    @commands.group(
        name="phone",
        brief="A dummy command for the commands.",
        invoke_without_command=True,
    )
    async def phone(self, ctx, user: Union[discord.Member, int] = None):
        user = user or ctx.author
        async with self.bot.processing(ctx):
            await asyncio.sleep(3)
            try:
                me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE id = $1", user.id)
            except:
                return await ctx.send(embed=PhoneEmbed(f"{user} does not have a phone number"))
            try:
                async with self.bot.embed(
                    title="Phone ",
                    description=f"{me['name']}'s number is {me['number']}",
                ) as embed:
                    await embed.send(ctx.channel)
            except:
                return await ctx.send(embed=PhoneEmbed(f"{user} does not have a phone number"))

    @phone.command(name="number", brief="Set someone's phone number!")
    @commands.is_owner()
    async def number_set(self, ctx, num: str, id: int):
        await self.bot.db.execute("UPDATE numbers SET number = $1 WHERE id = $2", num, id)
        await ctx.send("Changed number to {}".format(num))

    @phone.command(name="rcall", brief="Call Someone by their phone number (random edition)!")
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    async def rdial(self, ctx):
        try:
            me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % ctx.author.name)
        except:
            await ctx.send(
                embed=PhoneEmbed(
                    'The number you provided was not found or you dont have a number. create a number using "oahx phone create"'
                )
            )

        else:
            numbers = []
            for number in await self.bot.db.fetch("SELECT * FROM numbers"):
                numbers.append(number["number"])
            number = random.choice(numbers)
            number = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE number = $1", number)
            if number["number"] == me["number"]:
                return await ctx.send(embed=PhoneEmbed("The number was the same as your's. Try again."))
            channel_data = await self.try_channel(int(number["channel_id"]))
            try:
                me_channel_data = await self.try_channel(me["channel_id"])
            except:
                return await ctx.send(
                    embed=PhoneEmbed(
                        'The number was not found or you dont have a number. create a number using "oahx phone create"'
                    )
                )
            async with self.bot.processing(ctx):
                await asyncio.sleep(3)
                async with self.bot.embed(
                    title="Calling..",
                    description="<:phone:857956883464978432> Calling phone number `%s`" % number["number"],
                ) as embed:
                    await embed.send(ctx.channel)
            async with self.bot.embed(
                title="Incoming call..",
                description=f"<:phone:857956883464978432> There is an incoming call from `{me['name']} ({me['number']})`. They are calling `{number['name']}`, you can either type {ctx.prefix}decline or {ctx.prefix}pickup",
            ) as embed:
                await embed.send(channel_data)

            def s_check(m):
                return m.author.name == number["name"]

            try:
                message = await self.bot.wait_for("message", timeout=60.0, check=s_check)
                message = message.content.lower()
                if message == f"{ctx.prefix}pickup":
                    await channel_data.send("You are now talking with `{}`".format(me["name"]))
                    await me_channel_data.send("You are now talking with `{}`".format(number["name"]))
                    while True:

                        def check(m):
                            return (
                                m.author.id == number["id"]
                                and m.channel.id == number["channel_id"]
                                or m.author.id == me["id"]
                                and m.channel.id == me["channel_id"]
                            )

                        message = await self.bot.wait_for("message", check=check)
                        if message.content == f"{ctx.prefix}hangup":

                            await me_channel_data.send(embed=discord.Embed(description="Call ended"))
                            await channel_data.send(embed=discord.Embed(description="Call ended"))
                            break
                            return

                        elif message.author.name == number["name"]:
                            if message.content == "mute":

                                self.phone_mute = True
                                await me_channel_data.send("The other user have muted themselves.")
                            elif message.content == "unmute":

                                self.phone_mute = False
                                await me_channel_data.send("The other user have unmuted themselves.")
                                await me_channel_data.send(f"{number['name']}: {message.content}")
                            elif self.phone_mute:
                                pass
                            elif not self.phone_mute:
                                if message.attachments:
                                    attachment = message.attachments[0]
                                    if (
                                        attachment.content_type == "image/png"
                                        or attachment.content_type == "image/jpg"
                                        or attachment.content_type == "image/jpeg"
                                    ):
                                        my_io = io.BytesIO(await attachment.read())
                                        file = discord.File(my_io, "attachment.png")
                                        await me_channel_data.send(file=file)
                                    elif attachment.content_type == "video/mp4":

                                        my_io = io.BytesIO()
                                        my_content = await attachment.save(my_io)
                                        file = discord.File(my_io, "attachment.mp4")
                                        await me_channel_data.send(file=file)
                                if message.content == "reply":

                                    def p_check(m):
                                        return m.author.name == number["name"]

                                    await channel_data.send("Send the message id you want to reply to.")
                                    replied_message = await self.bot.wait_for(
                                        "message",
                                        check=lambda m: m.author.name == number["name"],
                                    )
                                    replied_message = int(replied_message.content)
                                    await channel_data.send("Send the reply content.")
                                    text_message = await self.bot.wait_for(
                                        "message",
                                        check=lambda m: m.author.name == number["name"],
                                    )
                                    text_message = text_message.content
                                    ch = await self.bot.fetch_channel(number["channel_id"])
                                    my_data = await ch.fetch_message(replied_message)
                                    await me_channel_data.send(f"> {my_data.content}\n\n\n{text_message}")

                                else:
                                    await me_channel_data.send(f"{number['name']}: {message.content}")

                        elif message.author.name == me["name"]:
                            if message.content.lower() == "mute":
                                await channel_data.send("The other user have muted themselves.")
                                self.me_mute = True
                            elif message.content.lower() == "unmute":
                                await channel_data.send("The other user have unmuted themselves.")
                                self.me_mute = False
                                await channel_data.send(f"{me['name']}: {message.content}")
                            elif self.me_mute:
                                pass
                            elif not self.me_mute:
                                if message.attachments:
                                    attachment = message.attachments[0]
                                    if (
                                        attachment.content_type == "image/png"
                                        or attachment.content_type == "image/jpg"
                                        or attachment.content_type == "image/jpeg"
                                    ):
                                        my_io = io.BytesIO(await attachment.read())
                                        file = discord.File(my_io, "attachment.png")
                                        await channel_data.send(file=file, content=message.content or None)
                                    elif attachment.content_type == "video/mp4":
                                        my_io = io.BytesIO()
                                        my_content = await attachment.save(my_io)
                                        file = discord.File(my_io, "attachment.mp4")
                                        await channel_data.send(file=file)
                            if message.content == "reply":

                                def m_check(m):
                                    return m.author.name == me["name"]

                                await me_channel_data.send("Send the message id you want to reply to.")
                                replied_message = await self.bot.wait_for("message", check=m_check)
                                replied_message = int(replied_message.content)
                                await me_channel_data.send("Send the reply content.")
                                text_message = await self.bot.wait_for("message", check=p_check)
                                text_message = text_message.content
                                my_data = await self.bot.http.get_message(me["channel_id"], replied_message)
                                await channel_data.send(f"> {my_data['content']}\n\n\n{text_message}")
                            else:
                                await channel_data.send(f"{me['name']}: {message.content}")

                elif message == f"{ctx.prefix}decline":
                    await ctx.send("Did not answer")
                    await channel_data.send("Call canceled.")
            except:
                async with self.bot.embed(title="Missed call...", description="You did not answer.") as embed:
                    return await embed.send(channel_data)

    @phone.command(name="call", brief="Call Someone by their phone number!")
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    async def _call(self, ctx, number: str):
        try:
            if number == "*661":
                channel = await self.try_channel(854670283457429524)
                return await self.call_support(ctx, channel)
            if number == "991":
                channel = await self.try_channel(854670283457429524)
                return await self.call_support(ctx, channel)
            try:
                author = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE id = $1", ctx.author.id)
                talking_to = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE number = $1", (number))
            except Exception as e:
                self.bot.dispatch("command_error", ctx=ctx, error=NotInDB(e))
                return await ctx.send(
                    embed=PhoneEmbed(
                        'The number you provided was not found or you dont have a number. create a number using "oahx phone create"'
                    )
                )
            if author["channel_id"] == talking_to["channel_id"]:
                return await ctx.send(embed=PhoneEmbed(f"You two are talking in the same channel."))
            self.calls[ctx.channel.id] = Call(
                await self.try_channel(talking_to["channel_id"]),
                recipients=[ctx.author, await self.bot.try_user(talking_to["id"])],
            )
            call: Call = self.calls[ctx.channel.id]
            talking_to_channel: discord.TextChannel = await self.try_channel(talking_to["channel_id"])
            author_channel: discord.TextChannel = await self.try_channel(author["channel_id"])
            while True:
                async with self.bot.embed(title="Calling...", description=f"Calling {number}...") as emb:
                    await emb.send(ctx.channel)
                async with self.bot.embed(
                    title="Incoming call...",
                    description=f"There is an incoming call from {author['name']}, are you sure you wanna pickup? `oahx pickup` to pickup or `oahx decline` to decline.",
                ) as emb:
                    from utils.subclasses import CustomEmbed
                    emb: CustomEmbed = emb
                    await emb.send(talking_to_channel, allowed_mentions=discord.AllowedMentions(users=True), content=f"<@{talking_to['id']}>")
                response = await self.bot.wait_for(
                    "message", check=lambda m: m.author.id == talking_to["id"] and m.channel.id == talking_to_channel.id, timeout=180
                )
                if response.content == "oahx pickup":
                    await ctx.send(f"You will be talking with `{str(call.recipients[1])}` today.")
                    await talking_to_channel.send(f"You will be talking with `{str(call.recipients[0])}` today."
                    )

                    def check(message: discord.Message):
                        return (
                            str(message.author) == str(call.recipients[1])
                            and message.channel.id == talking_to["channel_id"]
                        )

                    def author_check(message: discord.Message):
                        return (
                            str(message.author) == str(call.recipients[0])
                            and message.channel.id == author["channel_id"]
                        )

                    while True:
                        done, pending = await asyncio.wait(
                            [
                                self.bot.loop.create_task(self.bot.wait_for("message", check=check)),
                                self.bot.loop.create_task(self.bot.wait_for("message", check=author_check)),
                            ], return_when=asyncio.FIRST_COMPLETED
                        )

                        message = done.pop().result()
                        if message.content == "oahx hangup":
                            for future in pending:
                                future.cancel()
                            embed = discord.Embed(description="Call ended.")
                            await author_channel.send(embed=discord.Embed(description="Call ended."))
                            return await talking_to_channel.send(embed=embed)
                        if message.author.id == author["id"]:
                            await call.respond(ctx, user="user", message=f"{message.content}")
                        else:
                            await call.respond(ctx, user="me", message=message.content)
                        for future in pending:
                            future.cancel()
                else:
                    await talking_to_channel.send("Call declined. Call back if you want, or not.")
                    return await author_channel.send("Call declined. Call again if you want, or not.")
        except asyncio.TimeoutError:
            return await ctx.send("Missed call, call again later.")

    @phone.command(name="channel", brief="Change the channel where you receive calls")
    async def channel(self, ctx, change: str):
        if change == "change":
            try:
                async with self.bot.processing(ctx):
                    await asyncio.sleep(5)
                    await self.bot.db.execute(
                        "UPDATE numbers SET channel_id = $1 WHERE id = $2",
                        ctx.channel.id,
                        ctx.author.id,
                    )
                    await ctx.send("Channel changed to current channel!")
            except:
                await ctx.send(embed=PhoneEmbed("You don't have a phone number."))

    @phone.command(name="delete", brief="Delete your phone number!")
    async def delete(self, ctx):
        try:
            async with self.bot.processing(ctx):
                await asyncio.sleep(5)
                await self.bot.db.execute("DELETE FROM numbers WHERE id = $1", ctx.author.id)
                async with self.bot.embed(title="Success!", description="The operation was a success!") as embed:
                    await embed.send(ctx.channel)
        except:
            await ctx.send(embed=PhoneEmbed("You dont have a phone number."))

    @phone.command(name="create", brief="Create a phone number!")
    async def create(self, ctx):
        full_number = "0487"
        num_ber = 123456789087681083919371037197
        for i in range(7):
            full_number += random.choice(str(num_ber))
        async with self.bot.processing(ctx):
            await asyncio.sleep(5)
            data = await self.bot.db.fetch("SELECT * FROM numbers")
            for record in data:
                if record["id"] == ctx.author.id:
                    async with self.bot.embed(title="Error", description="You already have a phone number.") as embed:
                        return await embed.send(ctx.channel)
            await self.bot.db.execute(
                "INSERT INTO numbers(number, channel_id, name, id) VALUES ($1, $2, $3, $4)",
                full_number,
                ctx.channel.id,
                str(ctx.author),
                ctx.author.id,
            )
            async with self.bot.embed(
                title="Success!",
                description="The operation was a success, your phone number is `%s`, call `*661` for customer support."
                % full_number,
            ) as embed:
                return await embed.send(ctx.channel)

    @phone.group(
        name="contacts",
        invoke_without_command=True,
        brief="View, save, remove a contact in your contact book.",
    )
    async def contacts(self, ctx):
        if ctx.author.name in self.contact_book:
            async with self.bot.embed(
                title="Contacts",
                description=", ".join(self.contact_book[ctx.author.name]),
            ) as embed:
                await embed.send(ctx.channel)
        else:
            await ctx.send(embed=PhoneEmbed("You do not have any numbers saved."))

    @contacts.command(name="do", brief="Save/delete a phone number")
    async def do(self, ctx, option: str, name: str, number: str = None):
        if option == "save" and number != None:
            try:
                data = self.contact_book[ctx.author.name]
            except KeyError:
                self.contact_book[ctx.author.name] = []
                data = self.contact_book[ctx.author.name]
            data.append((name, number))
            async with self.bot.embed(title="Saved!", description="Saved number!") as embed:
                await embed.send(ctx.channel)
        elif option == "delete" and number == None:
            try:
                data = self.contact_book
                del data[ctx.author.name]
                async with self.bot.embed(
                    title="Deleted!",
                    description="Deleted that person from your contacts.",
                ) as embed:
                    await embed.send(ctx)
            except KeyError:
                self.contact_book[ctx.author.name] = []
                raise RuntimeError("You do not have that person saved in your contacts.")


def setup(bot):
    bot.add_cog(Contacts(bot))
