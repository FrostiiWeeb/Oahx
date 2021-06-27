import discord
from discord.ext import commands
from discord.ext import buttons
import tabulate, os

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
        	    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        	    await ctx.send(embed=embed, delete_after=60)        		
        	    
        	    return False
        	
        return True        
        
    @commands.group(hidden=True, invoke_without_command=True, brief="Some developer commands!")
    @commands.is_owner()
    async def dev(self, ctx):
        await ctx.send("Hey! These are the dev commands:\n`oahx dev maintenance (m)`")       
        
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
            if self.bot.owner_maintenance == True:
               if self.bot.maintenance:
               	self.bot.maintenance = False
               	await ctx.send("Maintenance is now off.")
               else:
                   if self.bot.owner_maintenance == True:
                   	self.bot.maintenance = True
                   	await ctx.send("Maintenance is now on.")
            else:
                pass
                
def setup(bot):
    bot.add_cog(Owner(bot))               		            		            