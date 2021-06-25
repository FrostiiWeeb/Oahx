import discord
from discord.ext import commands
from difflib import get_close_matches
import random
import traceback
import asyncio
from discord.ext.commands.cooldowns import BucketType
from typing import Union

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
        self.phone_mute = False
        self.me_mute = False
        self.using_support = False  
 
    async def try_channel(self, channel):
        channel_data = self.bot.get_channel(channel)
        if channel_data is None:
            channel_data = await self.bot.fetch_channel(channel)
        return channel_data        
                      
    async def get_users(self, ctx, other_number):
        phone_number = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE number = '%s'" % other_number)
        me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % ctx.author.name)   
        return {"me": me, "user": phone_number}
        
    async def get_channels(self, ctx, other_number):
        data = await self.get_users(ctx, other_number)
        me  = data["me"] 
        user = data["user"]    
        me_channel = await self.try_channel(me['channel_id'])  
        user_channel = await self.try_channel(user['channel_id'])     
        return {"me": me_channel, "user": user_channel}
        
    async def respond(self, ctx, other_mumber, content, user="me"):
        data = await self.get_channels(ctx, other_number)
        me = data["me"]
        target = data["user"]
        if user == "me":
            await me.send(content)
        elif user == "target":
            await target.send(content)                        
                                                                                 
    @commands.group(name="phone",brief="A dummy command for the commands.", invoke_without_command=True)
    async def phone(self, ctx, user : Union[discord.Member, int] = None):
        user = user or ctx.author
        try:
            me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % user.name)  
        except Exception:
            raise NumberNotFound(f"{user} does not have a phone number")
        try:
            async with self.bot.embed(title="Phone ", description=f"{me['name']}'s number is `%s`" % me["number"]) as embed:
                await embed.send(ctx.channel)
        except:
            raise NumberNotFound(f"{user} does not have a phone number")              
        
    @phone.command(name="call", brief="Call Someone by their phone number!") 
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)  
    async def call(self, ctx, number : str):
        if number == "911":
            if self.using_support:
                return await ctx.send("Support already being used.")
            self.using_support = True
            channel = await self.try_channel(854670283457429524)
            def check(m):
                return m.author.name == ctx.author.name or m.channel.id == 854670283457429524
            await channel.send("Hello, Someone is asking for help, please respond.")
            await ctx.send("Hello! Welcome to 911 phone support, how may we help you? If you did not realize, this is an automated message. The support team will get back to you shortly, so please wait, thanks!")
            while True:                                        
                message = await self.bot.wait_for("message", check=check)                      
                if message.content == "cancel":
                    self.using_support = False
                    await ctx.send("Call ended")    
                    await channel.send("Call ended") 
                    return
                elif message.author.name == ctx.author.name and message.channel.id != 854670283457429524:
                    await channel.send(f"{ctx.author.name}: {message.content}")
                elif message.channel.id == 854670283457429524:
                    await ctx.send(f"Support Team: {message.content}")
        try:
            phone_data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE number = '%s'" % number)
            me = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE name = '%s'" % ctx.author.name)
        except:
            raise NumberNotFound('The number you provided was not found or you dont have a number. create a number using "oahx phone create"')
        else:
            if me['channel_id'] == phone_data['channel_id']:
                raise ConnectionError(f"{me['name']}'s current channel id is the same as {phone_data['name']}'s current channel id.")
            try:
                channel_data = await self.try_channel(phone_data['channel_id'])
            except:
                raise NumberNotFound('The number you provided was not found or you dont have a number. create a number using "oahx phone create"')
            try:
                me_channel_data = await self.try_channel(me['channel_id'])
            except:
                raise NumberNotFound('The number you provided was not found or you dont have a number. create a number using "oahx phone create"')               
            async with self.bot.embed(title="Calling..", description="<:phone:857956883464978432> Calling phone number `%s`" % phone_data['number']) as embed:
                await embed.send(ctx.channel)
            async with self.bot.embed(title="Someone is calling..",description=f"<:phone:857956883464978432> `{me['name']} ({me['number']})` is calling `{phone_data['name']}`, do you want to pick up? [yes - no]") as embed:               
                await embed.send(channel_data)      
            def s_check(m):
                return m.author.name == phone_data['name']  
            try:
                message = await self.bot.wait_for("message", timeout=60.0, check=s_check)
                message = message.content.lower()
                if message == "yes":
                    await channel_data.send("You are now talking with `{}`".format(me["name"]))
                    await me_channel_data.send("You are now talking with `{}`".format(phone_data["name"]))
                    while True:
                        def check(m):
                            return m.author.name == phone_data["name"] and m.channel.id == phone_data["channel_id"] or m.author.name == me["name"] and m.channel.id == me["channel_id"]
                        message = await self.bot.wait_for("message",check=check)
                        if message.content == "cancel":
                            
                            await me_channel_data.send("Call ended")
                            await channel_data.send("Call ended")
                            break
                            return    
                                                                                          
                        elif message.author.name == phone_data["name"]:
                            if message.content == "mute":
                                
                                self.phone_mute = True
                                await me_channel_data.send("The other user have muted themselves.")                      
                            elif message.content == "unmute":
                                
                                self.phone_mute = False  
                                await me_channel_data.send("The other user have unmuted themselves.")                              
                                await me_channel_data.send(f"{phone_data['name']}: {message.content}")                            
                            elif self.phone_mute == True:
                                pass
                            elif self.phone_mute == False:
                                if message.content == "reply":
                                    def p_check(m):
                                        return m.author.name == phone_data['name']   
                                    await channel_data.send("Send the message id you want to reply to.")
                                    replied_message = await self.bot.wait_for("message", check=p_check)
                                    replied_message = int(replied_message.content)
                                    await channel_data.send("Send the reply content.")
                                    text_message = await self.bot.wait_for("message", check=p_check)
                                    text_message = text_message.content
                                    my_data = await self.bot.http.get_message(phone_data['channel_id'], replied_message)
                                    await me_channel_data.send(f"> {my_data['content']}\n\n\n{text_message}")
                                      
                                                                 
                                else:
                                    await me_channel_data.send(f"{phone_data['name']}: {message.content}")
                       
                        elif message.author.name == me["name"]:
                            if self.me_mute == True:
                                pass
                            elif self.me_mute == False:
                               
                                if message.content == "reply":
                                    def m_check(m):
                                        return m.author.name == me['name']   
                                    await me_channel_data.send("Send the message id you want to reply to.")
                                    replied_message = await self.bot.wait_for("message", check=m_check)
                                    replied_message = int(replied_message.content)
                                    await me_channel_data.send("Send the reply content.")
                                    text_message = await self.bot.wait_for("message", check=p_check)
                                    text_message = text_message.content
                                    my_data = await self.bot.http.get_message(me['channel_id'], replied_message)
                                    await channel_data.send(f"> {my_data['content']}\n\n\n{text_message}")
                                else:
                                    await channel_data.send(f"{me['name']}: {message.content}")                                   
                            elif message.content == "mute":
                                await channel_data.send("The other user have muted themselves.")                                    
                                self.me_mute = True
                            elif message.content == "unmute":
                                await channel_data.send("The other user have unmuted themselves.")                                    
                                self.me_mute = False
                                await channel_data.send(f"{me['name']}: {message.content}")                                                                                                                                  
                else:
                    await ctx.send("Did not answer") 
                    await channel_data.send("Call canceled.")  
                                                              
            except asyncio.TimeoutError:
                async with self.bot.embed(title="Call ended..", description="The call ended because no one responded..") as embed:
                    await embed.send(ctx.channel)
                    return await embed.send(channel_data)       

    @phone.command(name="channel", brief="Change the channel where you receive calls")   
    async def channel(self, ctx, change : str):
        if change == "change":
            try:
                await self.bot.db.execute("UPDATE numbers SET channel_id = $1 WHERE name = $2", ctx.channel.id, ctx.author.name)
                await ctx.send("Channel changed to current channel!")
            except:
                raise NumberNotFound("You dont have a phone number.")                                                     
            
    @phone.command(name="delete", brief="Delete your phone number!")
    async def delete(self, ctx):
        try:
            await self.bot.db.execute("DELETE FROM numbers WHERE name = $1", ctx.author.name)
            async with self.bot.embed(title="Success!", description="The operation was a success!") as embed:
                await embed.send(ctx.channel)            
        except:
            raise NumberNotFound("You dont have a phone number.")                                                                                                                                                                                        
    @phone.command(name="create", brief="Create a phone number!")
    async def create(self, ctx):
        full_number = "0487"
        num_ber = 123456789087681083919371037197
        for i in range(7):
            full_number += random.choice(str(num_ber)) 
        data = await self.bot.db.fetch("SELECT * FROM numbers") 
        for record in data:              
            if record["name"] == ctx.author.name:
                async with self.bot.embed(title="Error", description="You already have a phone number.") as embed:
                    return await embed.send(ctx.channel) 
        await self.bot.db.execute("INSERT INTO numbers(number, channel_id, name) VALUES ($1, $2, $3)", full_number, ctx.channel.id, ctx.author.name)                       
        async with self.bot.embed(title="Success!", description="The operation was a success, your phone number is `%s`" % full_number) as embed:
            return await embed.send(ctx)
            
def setup(bot):
    bot.add_cog(Contacts(bot))       