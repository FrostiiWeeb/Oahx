from discord.ext import commands
import discord
from typing import Union, Optional
import random, asyncio

import datetime
from discord.ext import commands
import datetime
from discord.ext import commands
from bot import Oahx
from discord.ui import Button, View
from datetime import datetime
import datetime
from typing import *
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: int
    description: str
    icon: str = None
    
class Inventory(BaseModel):
    items: List[Item]

class Shop(BaseModel):
    items: List[Item]

class Transaction:
    def __init__(self, payer: Union[discord.Member, discord.User], payee: Union[discord.Member, discord.User], amount: int, id: str) -> None:
        self.payer = payer
        self.payee = payee
        self.amount = amount
        self.id = id

    async def commit(self, ctx: commands.Context):
        async with ctx.bot.db.acquire() as c:
            try:
                author_record = await c.fetchrow("SELECT * FROM economy WHERE user_id = $1", self.payer.id)
                user_record = await c.fetchrow("SELECT * FROM economy WHERE user_id = $1", self.payee.id)
                author_data = (author_record['wallet'], author_record['bank'])
                user_data = (user_record['wallet'], user_record['bank'])
                author_after_wallet = author_data[0] - self.amount
                user_after_wallet = user_data[0] + self.amount
                if str(author_after_wallet).startswith("-"):
                    return await ctx.send("Do you really have enough? We all know you don't.")
                await c.execute("UPDATE economy SET wallet = $1 WHERE user_id = $2", author_after_wallet, self.payer.id)
                await c.execute("UPDATE economy SET wallet = $1 WHERE user_id = $2", user_after_wallet, self.payee.id)
                return await ctx.send(embed=discord.Embed(title="Transaction Completed.", description=f"{self.payee.mention}: Received {ctx.bot.emoji_dict['coin']}{self.amount:,}\n\nTransaction ID: {self.id}"))
            except:
                raise NotInDB("You or the user has not created an account. Create one with oahx account")


class PlaceButton(Button):
    def __init__(
        self,
        *,
        style=...,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
        view: discord.ui.View,
    ):
        super().__init__(
            style=discord.ButtonStyle.grey,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row,
        )
        self.__view = view
        self.ended = False

    async def callback(self, interaction: discord.Interaction):
        self.style = discord.ButtonStyle.success
        old_self = self
        self.__view.clear_items()
        self.__view.add_item(old_self)
        try:
            user = self.__view.context.author
        except:
            return await interaction.response.send_message("You don't have a bank account!", ephemeral=True)
        try:
            record = await self.view.context.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", user.id)
        except:
            return await interaction.response.send_message("You don't have a bank account!", ephemeral=True)
        money_given = random.randrange(100, 3000)
        await self.view.context.bot.db.execute(
            "UPDATE economy SET wallet = $1 WHERE user_id = $2", record["wallet"] + money_given, user.id
        )
        self.__view.stop()
        return await interaction.response.edit_message(
            view=self.__view,
            embed=discord.Embed(
                colour=self.__view.context.bot.colour,
                title=f"Searched {self.label}",
                description=f"You found {self.__view.context.bot.emoji_dict['coin']}{money_given:,}...",
            ),
        )


class SearchView(View):
    def __init__(self, *, timeout: Optional[float] = 180, bank_record=None, context=None):
        super().__init__(timeout=timeout)
        self.end_after = 20
        self.bank_record = bank_record
        self.context = context
        self.robbable_places = ["bedroom", "closet", "school", "area51", "source code"]
        for i in range(3):
            place = random.choice(self.robbable_places)
            self.robbable_places.remove(place)
            self.add_item(PlaceButton(label=place, view=self))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user and interaction.user.id in (
            self.context.bot.owner_ids,
            self.context.author.id,
        ):
            return True
        await interaction.response.send_message("This command wasnt ran by you, sorry!", ephemeral=True)
        return False


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
        deposited_money = money.replace(",", "")
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
        withdrawed_money = money.replace(",", "")
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
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def beg(self, ctx):
        money = random.randint(1, 201)
        give_money = random.choice([True, False, True, False])
        phrases = [
            "Im too poor",
            "Imagine begging lmao get a job kid",
            '"I only give money to my developers"\n - Oahx 2022',
            "Give me your phone first",
            "i dont have cash on me sorry",
        ]
        footers = ["he needs to beg too lol", "he's right", "why", "is this a robbery?", "is he sure?"]
        zipped = zip(phrases, footers)
        things = []
        for phrase, footer in zipped:
            things.append((phrase, footer))
        choice = random.choice(things)
        phrase, footer = choice[0], choice[1]
        try:
            data = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

            wallet = data["wallet"]
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
    @commands.cooldown(1, 20, commands.BucketType.user)
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
            give_money = random.randrange(author_record['wallet'])
            await self.bot.db.execute(
                "UPDATE economy SET wallet = $1 WHERE user_id = $2", user_record["wallet"] + give_money, user.id
            )
            await self.bot.db.execute(
                "UPDATE economy SET wallet = $1 WHERE user_id = $2", author_record["wallet"] - give_money, ctx.author.id
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

    @commands.command(name="search")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def search(self, ctx: commands.Context):
        return await ctx.send("**`Where do you wanna search?`**", view=SearchView(context=ctx))

    @commands.command()
    async def give(self, ctx: commands.Context, money: str, user: Union[discord.Member, str]):
        given_money = money.replace(",", "")
        final_money = int(given_money)
        transaction = Transaction(ctx.author, user, final_money, str((__import__("uuid")).uuid4()))
        return await transaction.commit(ctx)


def setup(bot):
    bot.add_cog(Economy(bot))
