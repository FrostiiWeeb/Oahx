import discord
from discord.ext import commands
import contextlib
import copy, string, random, base64


class Application(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="application", invoke_without_command=True, breif="Application command.")
    async def application(self, ctx):
        pass

    @application.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context):
        execute = True
        guild_id = ctx.guild.id
        questions = [
            "Mention a channel where the `application apply` command will be executed.",
            "Would you like to test the perfomance of the applicant in DMs? Respond with Yes or No. (`You will have to dm them yourself.`)",
        ]
        answers = []
        for i in questions:
            await ctx.send(i)
            answer = await self.bot.wait_for(
                "message",
                check=lambda m: str(m.author) == str(ctx.author) and m.channel == ctx.channel,
            )
            if i == "Mention a channel where the `application apply` command will be executed.":
                try:
                    print("i")
                    yes = int(answer.content[2:-1])
                    answers.append(yes)
                    execute = False
                except Exception:
                    return await ctx.send("The channel is incorrect. Try again.")
            answers.append(answer.content)
        channel_id = answers[0]
        skill_dm = answers[1]
        if skill_dm.lower() == "yes":
            skill_dm = True
        else:
            skill_dm = False
        try:
            await self.bot.db.execute(
                "INSERT INTO application_setup(guild_id, channel_id, skill_dm) VALUES ($1, $2, $3)",
                guild_id,
                channel_id,
                skill_dm,
            )
        except Exception as e:
            print(e)
            async with ctx.bot.embed(
                title="Error",
                description="Heyyy, there was an error. Please wait until it is fixed.",
            ) as emb:
                await emb.send(ctx.channel)

    @application.command(name="apply")
    @commands.has_permissions(send_messages=True)
    async def apply(self, ctx):
        setup = await self.bot.db.fetchrow("SELECT * FROM application_setup WHERE guild_id = $1", ctx.guild.id)
        if not setup:
            async with ctx.bot.embed(
                title="Error",
                description=f"Heyyy, there is no application setup here. Please notify the owner to do `{ctx.prefix}application setup`.",
            ) as emb:
                return await emb.send(ctx.channel)
        if not ctx.channel.id == setup["channel_id"]:
            async with ctx.bot.embed(
                title="Error",
                description=f"Heyyy, the channel you did the command in is not the application channel. Please execute it in the `{await self.bot.fetch_channel(setup['channel_id'])}`",
            ) as emb:
                return await emb.send(ctx.channel)
        questions = [
            "Why do you wanna join our staff team?",
            "Why should we choose you?",
            "How will you help us?",
            "Are you gonna follow all of our rules?",
        ]
        answers = []
        for i in questions:
            await ctx.send(i)

            answer = await self.bot.wait_for(
                "message",
                check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel,
            )
            answers.append(answer.content)
        await ctx.send("We have received your application, we will review it soon.")
        code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        why_staff = answers[0]
        why_choose_you = answers[1]
        follow_rule = answers[3]
        how_help = answers[2]
        message_bytes = str(ctx.author.id).encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        id = base64_bytes.decode("utf-8")
        await self.bot.db.execute(
            "INSERT INTO application(id, guild_id, channel_id, why_staff, why_choose_you, what_bring, how_help) VALUES ($1, $2, $3, $4, $5, $6, $7)",
            id,
            answer.guild.id,
            answer.channel.id,
            answers[0],
            answers[1],
            answers[3],
            answers[2],
        )
        join = ", ".join((why_staff, why_choose_you, follow_rule, how_help))
        user = await self.bot.try_user(ctx.guild.owner_id)
        async with ctx.bot.embed(
            title="New Application",
            description=f"**Author**: {str(ctx.author)}\n\nQuestion: Why do you wanna join our staff team?\n    - {why_staff}\nQuestion: Why should we choose you?\n    - {why_choose_you}\nQuestion: How will you help us?\n    - {how_help}\nQuestion: Will you follow all of our rules?\n    - {follow_rule}\n\n    - ID {id}",
        ) as emb:
            await emb.send(user)
            await emb.send(ctx.channel)

    @application.command(name="accept")
    @commands.guild_only()
    async def accept(self, ctx: commands.Context, id: str, *, message_accept: str):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("You do not have the valid permissions.")
        print("e")
        base64_bytes = id.encode("ascii")
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode("utf-8")
        print(message)
        user = await self.bot.try_user(int(message))
        async with self.bot.db.acquire() as db:
            guild_id = await db.fetchrow("SELECT guild_id FROM application WHERE id = $1", id)
            guild = await self.bot.fetch_guild(guild_id["guild_id"])
            await user.send(
                f"Hello! You have been accepted for staff on {guild.name}, we wanted to say: {message_accept}"
            )
        await ctx.send("Sent.")

    @application.command(name="decline")
    @commands.guild_only()
    async def decline(self, ctx: commands.Context, id: str, *, reason: str = "No Reason Provided"):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("You do not have the valid permissions.")
        print("e")
        base64_bytes = id.encode("ascii")
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode("utf-8")
        print(message)
        user = await self.bot.try_user(int(message))
        async with self.bot.db.acquire() as db:
            guild_id = await db.fetchrow("SELECT * FROM application WHERE id = $1", id)
            guild = await self.bot.fetch_guild(guild_id["guild_id"])
            await user.send(f"Hello! Sorry, you have been declined for staff on {guild.name} because {reason}.")
            await db.execute("DELETE FROM application WHERE id = $1", id)
        await ctx.send("Sent.")


def setup(bot):
    bot.add_cog(Application(bot))
