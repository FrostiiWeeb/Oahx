import discord, tabulate, os
from discord.ext import commands
from discord.ext import buttons
from utils.paginator import OahxPaginator
from jishaku.codeblocks import codeblock_converter
from aioconsole import aexec
from utils.CustomContext import CoolContext

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_check(self.maintenance_mode)
        
    async def maintenance_mode(self, ctx):
        if self.bot.maintenance:
        	if ctx.author.id in self.bot.owner_ids:
        		self.bot.owner_maintenance = True
        	else:
        	    embed = discord.Embed(description="Sorry, but maintenence mode is active.",colour=discord.Colour(0xffff00))
        	    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        	    await ctx.send(embed=embed, delete_after=60)        		
        	    
        	    return False
        	
        return True                               
        
    @commands.group(hidden=True, invoke_without_command=True, brief="Some developer commands!")
    @commands.is_owner()
    async def dev(self, ctx):
        await ctx.send("Hey! These are the dev commands:\n```oahx dev maintenance (m)\oahx dev eval (e)\n```")      
        
    @dev.command(hidden=True, brief="Evaluate some code!")
    async def eval(self, ctx, *, code : codeblock_converter):
        custom_context = CoolContext(message=ctx.message, prefix=await self.bot.get_prefix(ctx.message))
        custom_context.cog = self
        custom_context.bot = self.bot
        local_vars = {"ctx": custom_context, "discord": discord, "commands": commands, "bot": self.bot, "oahx": self.bot}
        await aexec(code, local_vars) 
           
        paginator = OahxPaginator(text=f"```py\n{result}\n```", colour=self.bot.colour, title="Evaluated")
        await paginator.paginate(custom_context)
        
    @dev.command(hidden=True,help="Confirm to use maintenance mode.",aliases=['cf'])
    async def confirm(self, ctx):
	    if ctx.author.id in self.bot.owner_ids:
	        
		    self.bot.owner_maintenance = True
		    embed = discord.Embed(title="You have been confirmed to use maintenance mode!", colour=self.bot.colour)	
		    await ctx.send(embed=embed)
	    else:
		    self.bot.owner_maintenance = False
		    embed = discord.Embed(title="You have not been confirmed to use maintenance mode.", colour=self.bot.colour)  
		    await ctx.send(embed=embed)
		    
    @dev.command(help="Turn on or off maintenance mode.",aliases=['maintenance'], hidden=True)
    @commands.is_owner()
    async def m(self, ctx):
            if self.bot.owner_maintenance:
               if self.bot.maintenance:
               	self.bot.maintenance = False
               	await ctx.send("Maintenance is now off.")
               else:
                   if self.bot.owner_maintenance:
                   	self.bot.maintenance = True
                   	await ctx.send("Maintenance is now on.")
            else:
                pass
                
def setup(bot):
    bot.add_cog(Owner(bot))               		            		            
