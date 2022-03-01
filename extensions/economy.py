from discord.ext import commands
import discord
from typing import Union, Optional
import random, asyncio

import datetime
from discord.ext import commands
import datetime
from discord.ext import commands
from bot import Oahx


class NotInDB(Exception):
    def __init__(self, message="You have not created a bank account yet."):
        super().__init__(message)
        self.msg = message


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: Oahx = bot

    @commands.command(name="account", aliases=["acc"])
    async def cracc(self, ctx):
        accounts = await ctx.bot.db.fetch("SELECT * FROM economy")
        for rec in accounts:
            if rec["user_id"] == ctx.author.id:
                async with ctx.bot.embed(title="Error", description="You already have an account.") as emb:
                    return await emb.send(ctx.channel)
        await self.bot.db.execute(
            "INSERT INTO economy(user_id, wallet, bank) VAlUES ($1, $2, $3)",
            ctx.author.id,
            0,
            0,
        )
        async with self.bot.processing(ctx):
            await asyncio.sleep(3)
            async with ctx.bot.embed(title="Bank", description=f"You have created an account!") as emb:
                return await emb.send(ctx.channel)

    @commands.command(aliases=["bal"], brief="Get the balance of a user!")
    async def balance(self, ctx, user: Union[discord.Member, int] = None):
        user = user or ctx.author

        try:
            data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", user.id)

            wallet = int(data["wallet"])
            bank = int(data["bank"])
            networth = int(wallet) + int(bank)

            await ctx.send(
                embed=discord.Embed(
                    title=f"{user.name}'s balance",
                    description=f"**Wallet**: {self.bot.emoji_dict['coin']} {wallet:,}\n**Bank**: {self.bot.emoji_dict['coin']} {bank:,}\n**Networth**: {self.bot.emoji_dict['coin']} {networth:,}",
                )
            )
        except:
            raise NotInDB()

    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, money: str):
        deposited_money = money.strip(",")
        final_money = int(deposited_money)
        async with self.bot.db.acquire() as c:
            bank = await c.fetchrow("SELECT bank FROM economy WHERE user_id = $1", ctx.author.id)
            new_bank = final_money + bank["bank"]
            wallet = await c.fetchrow("SELECT wallet FROM economy WHERE user_id = $1", ctx.author.id)
            new_wallet = wallet["wallet"] - final_money
            if str(new_wallet).startswith("-"):
                return await ctx.send(
                    embed=discord.Embed(
                        description="You don't have that kind of money!",
                        colour=ctx.bot.colour,
                    )
                )
            else:
                new_wallet = int(new_wallet)
            await c.execute(
                "UPDATE economy SET wallet = $1, bank = $2 WHERE user_id = $3;",
                new_wallet,
                new_bank,
                ctx.author.id,
            )
            async with ctx.bot.embed(
                title="ATM",
                description=f"ATM: Deposited {self.bot.emoji_dict['coin']} {money}.",
            ) as emb:
                return await emb.send(ctx.channel)

    @commands.command(aliases=["with"])
    async def withdraw(self, ctx, money: str):
        withdrawed_money = money.strip(",")
        final_money = int(withdrawed_money)
        async with self.bot.db.acquire() as c:
            bank = await c.fetchrow("SELECT bank FROM economy WHERE user_id = $1", ctx.author.id)
            new_bank = bank["bank"] - final_money
            wallet = await c.fetchrow("SELECT wallet FROM economy WHERE user_id = $1", ctx.author.id)
            new_wallet = wallet["wallet"] + final_money
            if str(new_bank).startswith("-"):
                return await ctx.send(
                    embed=discord.Embed(
                        description="You don't have that kind of money!",
                        colour=ctx.bot.colour,
                    )
                )
            else:
                new_bank = int(new_bank)
            await c.execute(
                "UPDATE economy SET wallet = $1, bank = $2 WHERE user_id = $3;",
                new_wallet,
                new_bank,
                ctx.author.id,
            )
            async with ctx.bot.embed(
                title="ATM",
                description=f"ATM: Withdrew **{self.bot.emoji_dict['coin']}{money}**.",
            ) as emb:
                return await emb.send(ctx.channel)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def beg(self, ctx):
        money = random.randint(1, 201)
        give_money = random.choice([True, False, True, False])
        phrases = [
            "Im too poor",
            "Imagine begging lmao get a job kid",
            '"I only give money to my developers"\n - Oahx 2022',
            "Give me your phone first",
        ]
        footers = ["he needs to beg too lol", "he's right", "why", "is this a robbery?"]
        zipped = zip(phrases, footers)
        things = []
        for phrase, footer in zipped:
            things.append((phrase, footer))
        choice = random.choice(things)
        phrase, footer = choice[0], choice[1]
        try:
            data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

            wallet = data["wallet"]
            bank = data["bank"]
            if not give_money:
                return await ctx.send(embed=(discord.Embed(title="LMAO", description=phrase)).set_footer(text=footer))
            await ctx.send(
                embed=discord.Embed(
                    description=f"You earned **{money}{self.bot.emoji_dict['coin']}**!",
                )
            )
            await self.bot.db.execute(
                f"UPDATE economy SET wallet = $1 WHERE user_id = $2",
                wallet + money,
                ctx.author.id,
            )
        except Exception as e:
            print(e)
            raise NotInDB()

    @commands.command()
    async def rob(self, ctx: commands.Context, user: Union[discord.Member, int]):
        if user == ctx.author:
            return await ctx.send("You wanted to steal from yourself? Nahhhh that won't happen.")
        try:
            user_record = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", user.id)
            author_record = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)
        except:
            raise NotInDB("You or the user has not created a bank account.")
        if user_record["wallet"] < 500:
            return await ctx.send("They don't have more than 500 in their wallet, not worth it man...")
        if author_record["wallet"] < 500:
            return await ctx.send("You must have 500+ in your wallet to rob.")
        money_to_rob = random.randrange(int(user_record["wallet"]))
        robbed = random.choice([True, False, True, False])
        if not robbed:
            await self.bot.db.execute(
                "UPDATE economy SET wallet = $1 WHERE user_id = $2", user_record["wallet"] + 250, user.id
            )
            await self.bot.db.execute(
                "UPDATE economy SET wallet = $1 WHERE user_id = $2", author_record["wallet"] - 250, ctx.author.id
            )
            return await ctx.reply(
                f"Your robbery failed, and got caught by the police.. you paid the user {self.bot.emoji_dict['coin']}250."
            )
        await self.bot.db.execute(
            "UPDATE economy SET wallet = $1 WHERE user_id = $2", author_record["wallet"] + money_to_rob, ctx.author.id
        )
        await self.bot.db.execute(
            "UPDATE economy SET wallet = $1 WHERE user_id = $2", user_record["wallet"] - money_to_rob, user.id
        )
        return await ctx.send(f"You got away with {self.bot.emoji_dict['coin']}{money_to_rob}...")


def setup(bot):
    bot.add_cog(Economy(bot))
