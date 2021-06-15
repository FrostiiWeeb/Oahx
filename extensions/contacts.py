import discord
from discord.ext import commands
from difflib import get_close_matches
import random
import traceback
import asyncio
from discord.ext.commands.cooldowns import BucketType


class Contacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute = False
        
    async def try_channel(self, channel):
        channel_data = self.bot.get_channel(channel)
        if channel_data is None:
            channel_data = await self.bot.fetch_channel(channel)
        return channel_data 
               
    @commands.group(name="phone",brief="A dummy command for the commands.", invoke_without_command=True)
    async def phone(self, ctx):
        me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % ctx.author.name)  
        async with self.bot.embed(title="Phone ", description="Your phone number is `%s`" % me["number"]) as embed:
            await embed.send(ctx.channel)      
        
    @phone.command(name="call", brief="Call Someone by their phone number!") 
    @commands.max_concurrency(1, per=BucketType.channel, *, wait=False)  
    async def call(self, ctx, number : str):
        if number == "991":
            channel = await self.try_channel(817471364302110731)
            def check(m):
                roles = [r.name for r in m.author.roles]
                return m.author.name == ctx.author.name or m.channel.id == 817471364302110731
            await channel.send("Someone is asking for help, please respond.")
            await ctx.send("Please tell us your question, problem.")
            while True:                                        
                message = await self.bot.wait_for("message", check=check)  
            
                roles = [r.name for r in message.author.roles]            
                if message.content == "cancel":
                    await ctx.send("Call ended")    
                    await channel.send("Call ended") 
                    return
                elif message.author.name == ctx.author.name and message.channel.id != 817471364302110731:
                    await channel.send(f"{ctx.author.name}: {message.content}")
                elif message.channel.id == 817471364302110731:
                    await ctx.send(f"Support Team: {message.content}")
        try:
            phone_data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE number = '%s'" % number)
            me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % ctx.author.name)
        except Exception:
            traceback.print_exc()
            async with self.bot.embed(title="Number Not Found", description="The phone number that was provided is not correct or you do not have one.") as embed:
                return await embed.send(ctx.channel)
        else:
            channel_data = await self.try_channel(phone_data['channel_id'])
            me_channel_data = await self.try_channel(me['channel_id'])
            async with self.bot.embed(title="Calling..", description="Calling phone number `%s`" % phone_data['number']) as embed:
                await embed.send(ctx.channel)
            async with self.bot.embed(title="Someone is calling..",description=f"`{me['name']} ({me['number']}` is calling `{phone_data['name']}`, do you want to pick up? [yes - no]") as embed:               
                await embed.send(channel_data)      
            def check(m):
                return m.author.name == phone_data['name']  
            try:
                message = await self.bot.wait_for("message", timeout=30.0, check=check)
                message = message.content.lower()
                if message == "yes":
                    await channel_data.send("You are now talking with `{}`".format(me["name"]))
                    await me_channel_data.send("You are now talking with `{}`".format(phone_data["name"]))
                    while True:
                        def check(m):
                            return m.author.name == phone_data["name"] or m.author.name == me["name"] and m.channel.id == phone_data["channel_id"] or m.channel.id == me["channel_id"]
                        message = await self.bot.wait_for("message",check=check)
                        if message.content == "cancel":
                            await me_channel_data.send("Call ended")
                            await channel_data.send("Call ended")
                            break
                            return    
                                                                                          
                        elif message.author.name == phone_data["name"]:
                            if self.mute == True:
                                pass
                            elif self.mute == False:
                                await me_channel_data.send(f"{phone_data['name']}: {message.content}")
                            elif message.content == "mute":
                                self.mute = True                        
                            elif message.content == "unmute":
                                self.mute = False                       
                                await me_channel_data.send(f"{phone_data['name']}: {message.content}")
                        elif message.author.name == me["name"]:
                            if self.mute == True:
                                pass
                            elif self.mute == False:
                                await channel_data.send(f"{me['name']}: {message.content}")
                            elif message.content == "mute":
                                self.mute = True                        
                            elif message.content == "unmute":
                                self.mute = False                                 
                                await channel_data.send(f"{me['name']}: {message.content}") 
                else:
                    await ctx.send("Did not answer") 
                    await channel_data.send("Call canceled.")                                            
            except asyncio.TimeoutError:
                async with self.bot.embed(title="Call ended..", description="The call ended because no one responded..") as embed:
                    await embed.send(ctx.channel)
                    await embed.send(channel_data)       

    @phone.command(name="channel", brief="Change the channel where you receive calls")   
    async def channel(self, ctx, change : str):
        if change == "change":
            await self.bot.db.execute("UPDATE numbers SET channel_id = $1 WHERE name = $2", ctx.channel.id, ctx.author.name)
            await ctx.send("Channel changed to current channel!")
            
    @phone.command(name="delete", brief="Delete your phone number!")
    async def delete(self, ctx):
        try:
            await self.bot.db.execute("DELETE FROM numbers WHERE name = $1", ctx.author.name)
            async with self.bot.embed(title="Success!", description="The operation was a success!") as embed:
                await embed.send(ctx.channel)            
        except:
            async with self.bot.embed(title="Error", description="You do not have a phone number.") as embed:
                await embed.send(ctx.channel)                                                                                                                                                                                  
    @phone.command(name="create", brief="Create a phone number!")
    async def create(self, ctx):
        full_number = "0487"
        num_ber = 123456789087681083919371037197
        for i in range(7):
            full_number += random.choice(str(num_ber))       
        await self.bot.db.execute("INSERT INTO numbers(number, channel_id, name) VALUES ($1, $2, $3)", full_number, ctx.channel.id, ctx.author.name)
        async with self.bot.embed(title="Success!", description="The operation was a success, your phone number is `%s`" % full_number) as embed:
            return await embed.send(ctx)
            
def setup(bot):
    bot.add_cog(Contacts(bot))       