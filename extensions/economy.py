from discord.ext import commands
import discord
from typing import Union, Optional
import random, asyncio

import datetime
from discord.ext import commands
import datetime
from discord.ext import commands

class NotInDB(Exception):
    def __init__(self, message = "You havent created a bank account yet."):
        super().__init__("You havent created a bank account yet.")
        self.msg = "You havent created a bank account yet."	

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(name="account", aliases=["acc"])
	async def cracc(self, ctx):
	   accounts = await ctx.bot.db.fetch("SELECT * FROM economy")
	   for rec in accounts:
	   	if rec['user_id'] == ctx.author.id:
    			async with ctx.bot.embed(title="Error", description="You already have an account.") as emb:
    				return await emb.send(ctx.channel)  				
	   await self.bot.db.execute("INSERT INTO economy(user_id, wallet, bank) VAlUES ($1, $2, $3)", ctx.author.id, 100, 0)
	   async with self.bot.processing(ctx):
	   	await asyncio.sleep(3)
	   	async with ctx.bot.embed(title="Bank", description="You have created an account! And take the extra **$100**!") as emb:
	   		return await emb.send(ctx.channel)    			      				
		
	@commands.command(aliases=['bal'], brief="Get the balance of a user!")
	async def balance(self, ctx, user : Union[discord.Member, int] = None):
		user = user or ctx.author
		
		try:
			data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", user.id)
			
			wallet = data['wallet']
			bank = data['bank']
			
			await ctx.send(embed=discord.Embed(title=f"{user.name}'s balance", description=f"Wallet: **{self.bot.emoji_dict['coin']}{wallet} **\nBank: **{self.bot.emoji_dict['coin']}{bank}**", colour=ctx.bot.colour))
		except:
			raise NotInDB()
			
	@commands.command(aliases=["dep"])
	async def deposit(self, ctx, money : str):
		deposited_money = money.strip(",")
		final_money = int(deposited_money)
		async with self.bot.db.acquire() as c:
			bank = await c.fetchrow("SELECT bank FROM economy WHERE user_id = $1", ctx.author.id)		
			new_bank = final_money + bank['bank']
			wallet = await c.fetchrow("SELECT wallet FROM economy WHERE user_id = $1", ctx.author.id)
			new_wallet = wallet['wallet'] - final_money
			if str(new_wallet).startswith("-"):
				await ctx.send(embed=discord.Embed(description="You don\'t have that kind of money!", colour=ctx.bot.colour))
			else:
				new_wallet = int(new_wallet)
			await c.execute("UPDATE economy SET wallet = $1, bank = $2 WHERE user_id = $3;", new_wallet, new_bank, ctx.author.id)
			async with ctx.bot.embed(title="ATM", description=f"ATM: Deposited **{self.bot.emoji_dict['coin']}{money}**.") as emb:
				return await emb.send(ctx.channel)
			
			
	@commands.command(aliases=["with"])
	async def withdraw(self, ctx, money : str):
		withdrawed_money = money.strip(",")
		final_money = int(withdrawed_money)
		async with self.bot.db.acquire() as c:
			bank = await c.fetchrow("SELECT bank FROM economy WHERE user_id = $1", ctx.author.id)		
			new_bank = final_money - bank['bank']
			wallet = await c.fetchrow("SELECT wallet FROM economy WHERE user_id = $1", ctx.author.id)
			new_wallet = wallet['wallet'] + final_money
			if str(new_bank).startswith("-"):
				await ctx.send(embed=discord.Embed(description="You don\'t have that kind of money!", colour=ctx.bot.colour))
			else:
				new_bank = int(new_bank)
			await c.execute("UPDATE economy SET wallet = $1, bank = $2 WHERE user_id = $3;", new_wallet, new_bank, ctx.author.id)
			async with ctx.bot.embed(title="ATM", description=f"ATM: Withdrew **{self.bot.emoji_dict['coin']}{money}**.") as emb:
				return await emb.send(ctx.channel)						
	
	@commands.command()
	@commands.cooldown(1, 20, commands.BucketType.user)
	async def beg(self, ctx):
		money = random.randint(1, 201)
		try:
			data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
			
			wallet = data['wallet']
			bank = data['bank']
			
			await ctx.send(embed=discord.Embed(description=f"You earned **{self.bot.emoji_dict['coin']}**!", colour=ctx.bot.colour))
			await self.bot.db.execute(f"UPDATE economy SET wallet = $1 WHERE user_id = $2", wallet + money, ctx.author.id)
		except Exception as e:
			print(e)
			raise NotInDB()					


def setup(bot):
	bot.add_cog(Economy(bot))									