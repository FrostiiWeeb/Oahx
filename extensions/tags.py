import discord
from discord.ext import commands
import asyncio
from typing import Optional
from typing import Union
from asyncpg import UniqueViolationError
import discord
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext import menus
from difflib import get_close_matches

class TagName(commands.clean_content):
    def __init__(self, *, lower=False):
        self.lower = lower
        super().__init__()

    async def convert(self, ctx, argument):
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument('Missing tag name.')

        if len(lower) > 100:
            raise commands.BadArgument('Tag name is a maximum of 100 characters.')			


class TagSource(ListPageSource):
		def __init__(self, ctx, data):
			self.lmao = ctx
			
			super().__init__(data, per_page=4)
		
		async def write_page(self, menu, fields=[]):
			embed = discord.Embed(title="Tags", color=self.lmao.bot.colour)
			for name in fields:
				embed.add_field(name=name, value="______", inline=False)
			return embed
		
		async def format_page(self, menu, entries):
			fields = []
			for entry in entries:
				fields.append(entry)
			
			return await self.write_page(menu, fields)
			
class TagPages(MenuPages):
    def __init__(self, source):
        super().__init__(source, delete_message_after=True, timeout=60.0)			

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def too_long(self, ctx):
        async with self.bot.embed(title="Uhhh", description="You took too long! Try again with {ctx.prefix}{ctx.command.name}.") as emb:
            await emb.send(ctx.channel)
        
    async def get_user_tags(self, ctx, user):
        tag_list = []
        for db in await self.bot.db.fetch("SELECT * FROM tags WHERE author = $1", str(user)):
            tag_list.append(db["name"])		
        await TagPages(source=TagSource(ctx=ctx, data=tag_list)).start(ctx)
        
    async def get_global_tags(self, ctx):
        tag_list = []
        for db in await self.bot.db.fetch("SELECT * FROM tags;"):
            tag_list.append(db["name"])
        await TagPages(source=TagSource(ctx=ctx, data=tag_list)).start(ctx)
        
    @commands.group(invoke_without_command=True, help="Get the content for a tag.")
    async def tag(self, ctx, *, name : str):
        try:
            data = await self.bot.db.fetchrow("SELECT content FROM tags WHERE name = $1", str(name.lower()))
            await ctx.send(data["content"])			
        except Exception as e:
            tags = [db['name'] for db in await self.bot.db.fetch("SELECT * FROM tags")]
            matches = get_close_matches(name, tags)
            if len(matches) > 0:
                await ctx.send(f"A tag with that name does not exist, did you mean \"{matches[0]}\"?")
            else:
                await ctx.send("A tag with that name does not exist.")
    
    @commands.command()
    async def tags(self, ctx):
        """
		Get the tags of the author (`ctx.author`)
		"""
        await self.get_user_tags(ctx, ctx.author)
        
    @tag.command()
    async def claim(self, ctx, *, tag : str):
        tag = tag.lower()
        try:
            data = await self.bot.db.fetchrow("SELECT author FROM tags WHERE name = $1", str(tag))
            if not data['author'] == str(ctx.author):
                await ctx.send("The tag owner is still here!")
            else:
                await ctx.send("Transfered tag to ya!")
                await self.bot.db.execute("UPDATE tags SET author = $1 WHERE user_id = $1", str(ctx.author), data['user_id'])	
        except Exception as e:
            print(e)
            tags = [db['name'] for db in await self.bot.db.fetch("SELECT * FROM tags")]
            matches = get_close_matches(name, tags)
            if len(matches) > 0:
                await ctx.send(f"A tag with that name does not exist, did you mean \"{matches[0]}\"?")
            else:
                await ctx.send("A tag with that name does not exist.")		
                
    @tag.command()
    async def edit(self, ctx, tag : TagName(lower=True), *, content : commands.clean_content):
        """
		Edit a tag.
		"""
        try:
            data = await self.bot.db.fetchrow("UPDATE tags SET content = $1 WHERE name = $2 AND author = $3", content, str(tag), str(ctx.author))
            await ctx.send(f"Edited `{tag}`!")			
        except Exception as e:
            print(e)
            await ctx.send("A tag with that name does not exist or you don\'t own it.")		
                
    @tag.command()
    async def transfer(self, ctx, target : discord.Member, *, tag : TagName(lower=True)):
        """
        Transfer a tag to another member.
        """
        try:
            data = await self.bot.db.fetchrow("UPDATE tags SET author = $1 WHERE name = $2 AND user_id = $3", str(target), str(tag), ctx.author.id)
            await ctx.send(f"Transfered `{tag}`!")			
        except Exception as e:
            print(e)
            await ctx.send("A tag with that name does not exist or you don\'t own it.")
                
    @tag.command()
    async def info(self, ctx, *, tag : str):
        """
        Get the info of a tag.
        """
        tag = str(tag.lower())
        try:
            data = await self.bot.db.fetchrow("SELECT * FROM tags WHERE name = $1", str(tag))
            owner = data['author']
            name = data['name']		
            async with ctx.bot.embed(description=f"**Name:**\n{name}\n**Owner:**\n{owner}\n") as emb:
                await emb.send(ctx)		
        except Exception as e:
            print(e)
            await ctx.send("A tag with that name does not exist.")		
            
    @tag.command()
    async def list(self, ctx):
        await self.get_global_tags(ctx)
        
    @tag.command()
    async def make(self, ctx):
        db = self.bot.db
        try:
            await ctx.send("Heyyoo! You want to make a tag, ay? Alright. Answer these questions.")
            await ctx.send("What do you want the tag name to be?")
            message = await self.bot.wait_for("message", check=lambda m : m.author == ctx.author)
        except asyncio.TimeoutError:
            return await self.too_long(ctx)
        else:
            name = message.content.lower()
        try:
            await ctx.send(f"Ayyy, the tag name will be {name}, now what do you want the tag content to be?")
            message = await self.bot.wait_for("message", check=lambda m : m.author == ctx.author)
        except asyncio.TimeoutError:
            return await self.too_long(ctx)
        else:
            content = message.content
        async with db.acquire() as db:
            tags = [tag["name"] for tag in await db.fetch("SELECT * FROM tags")]
            if name in tags:
                return await ctx.send(f"Heyyy mate, the tag {name} already exists.")
            async with self.bot.embed(title="Created", description="Heyyy, the tag was created.") as emb:
                await emb.send(ctx.channel)
            # await db.execute("DELETE FROM cooldown_channel WHERE channel_id = $1 AND command = $2", ctx.channel.id, ctx.command.name)
            await db.execute("INSERT INTO tags(user_id, name, content, author) VALUES ($1, $2, $3, $4)", ctx.author.id, name, content, str(ctx.author))
        
        
						
															
def setup(bot):
	bot.add_cog(Tags(bot))