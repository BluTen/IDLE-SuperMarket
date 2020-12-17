# Imports of Built In Libraries
from asyncio import TimeoutError
from datetime import datetime, timedelta
from platform import python_version
from time import time, ctime

# Imports of Downloaded Libraries
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord import Embed, Color
from discord.ext.commands import Cog, command, check
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from psutil import Process, virtual_memory

# Imports of Self-Made Libraries
from ..db import db


class Profile(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="start",
	         aliases=['create', 'sat'],
	         description="To creates a profile of the person who used it",
	         brief="`{0}start`")
	async def create_profile(self, ctx):
		player = db.field("SELECT member_id FROM Profile WHERE member_id = ?", ctx.message.author_id)
		pfx = db.field("SELECT prefix FROM Guild_Info WHERE guild_id = ?", ctx.guild.id)

		if player is None:

			db.execute("INSERT INTO Profile (member_id) VALUES(?)", ctx.message.author_id)
			e = Embed(title=f"{ctx.message.author}, You now have a plot",
			          color=Color(0xff0000),
			          timestamp=datetime.utcnow())
			e.set_thumbnail(url=ctx.message.author.avatar_url)
			e.add_field(name="So you started a Business, A SuperMarket",
			            value="So now you have a plot and thought to become a worlds biggest business tycoon but"
			                  " there is no building to start",
			            inline=False)
		else:
			ctx.send(f"You already have a SuperMarket,\n"
			         f"If you wanna check the stats and info of you SuperMarket then use `{ctx.prefix}marketinfo`")
			# todo Finish profile commands

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(str(__name__).split(".")[-1])


def setup(bot):
	bot.add_cog(Profile(bot))
