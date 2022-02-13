import asyncpg
from discord.ext import commands
import discord
from bot import Oahx
import traceback
import sys

class Logging(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot : Oahx = bot
		self.bot.db = self.bot.db
		
	@commands.Cog.listener()
	async def on_member_ban(self, guild: discord.Guild, user: discord.User):
		user_name = str(user)
		guild_id = guild.id

		row = await self.bot.db.fetchrow("SELECT * FROM logging WHERE guild_id = $1", guild_id)
		if not row:
			return
		"""
		on_member_remove
		on_member_unban"""
		channel = await self.bot.try_channel(row["channel_id"])
		def predicate(event : discord.AuditLogEntry):
			return event.action is discord.AuditLogAction.ban
		
		try:
			event : discord.AuditLogEntry = await guild.audit_logs(limit=1).find(predicate)
			async with self.bot.embed(title="Member Banned.", description=f"User: {event.target} `<@{user.id}>`\nReason: {event.reason}\nAction: Member Ban\nModerator: {event.user}") as emb:
				emb.embed.set_author(name=user_name, icon_url=user.avatar.url)
				return await emb.send(channel)
		except:
			traceback.print_exc(file=sys.stderr)

	@commands.Cog.listener()
	async def on_member_unban(self, guild : discord.Guild, user: discord.Member):
		user_name = str(user)
		guild_id = guild.id

		row = await self.bot.db.fetchrow("SELECT * FROM logging WHERE guild_id = $1", guild_id)
		if not row:
			return
		"""
		on_member_remove
		on_member_unban"""
		channel = await self.bot.try_channel(row["channel_id"])
		def predicate(event : discord.AuditLogEntry):
			return event.action is discord.AuditLogAction.unban
		
		try:
			event : discord.AuditLogEntry = await guild.audit_logs(limit=1).find(predicate)
			async with self.bot.embed(title="Member Unbanned.", description=f"User: {user_name} `<@{user.id}>`\nReason: {event.reason}\nAction: Member UnBan\nModerator: {event.user}") as emb:
				emb.embed.set_author(name=user_name, icon_url=user.avatar.url)
				return await emb.send(channel)
		except:
			traceback.print_exc(file=sys.stderr)

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		guild : discord.Guild = member.guild
		user_name = str(member)
		guild_id = guild.id

		row = await self.bot.db.fetchrow("SELECT * FROM logging WHERE guild_id = $1", guild_id)
		if not row:
			return
		"""
		on_member_remove
		on_member_unban"""
		channel = await self.bot.try_channel(row["channel_id"])
		def predicate(event : discord.AuditLogEntry):
			return event.action is discord.AuditLogAction.kick
		
		try:
			event : discord.AuditLogEntry = await guild.audit_logs(limit=1).find(predicate)
			async with self.bot.embed(title="Member Kicked.", description=f"User: {user_name} `<@{member.id}>`\nReason: {event.reason}\nAction: Member Kick\nModerator: {event.user}") as emb:
				emb.embed.set_author(name=user_name, icon_url=member.avatar.url)
				return await emb.send(channel)
		except:
			traceback.print_exc(file=sys.stderr)

def setup(bot : Oahx):
	bot.add_cog(Logging(bot))