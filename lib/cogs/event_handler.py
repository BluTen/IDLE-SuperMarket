# Imports of Built In Libraries
from asyncio import TimeoutError
from datetime import datetime, timedelta
from platform import python_version
from time import time, ctime

# Imports of Downloaded Libraries
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord import Embed, Color, ClientUser
from discord.ext.commands import Cog, group
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from psutil import Process, virtual_memory

# Imports of Self-Made Libraries
from ..db import db


class EventHandler(Cog):
	def __init__(self, bot):
		self.bot = bot

	# @Cog.listener()
	# async def on_message(self, message):
	# 	print(message.content)
	# 	await self.bot.process_commands(message)

	@Cog.listener()
	async def on_guild_join(self, guild):
		db.execute("INSERT INTO Guild_Settings(guild_id, prefix) VALUES(?, ?)", int(guild.id), "!m")

	@Cog.listener()
	async def on_guild_remove(self, guild):
		db.execute("DELETE FROM Guild_Settings WHERE guild_id = ?", guild.id)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(str(__name__).split(".")[-1])


def setup(bot):
	bot.add_cog(EventHandler(bot))