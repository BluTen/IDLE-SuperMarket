# Imports of Built In Libraries
from asyncio import TimeoutError, create_task
from datetime import datetime, timedelta
from platform import python_version
from time import time, ctime
from typing import Union

# Imports of Downloaded Libraries
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord import Embed, Color
from discord.ext.commands import Cog, group, Command, Group
from discord.ext.commands import has_permissions
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from DiscordUtils.Pagination import CustomEmbedPaginator

# Imports of Self-Made Libraries
from ..db import db


class Help(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.gameplay_cogs = [self.bot.get_cog("Profile"), ]
		self.categories = [("gameplay", self.gameplay_cogs), ]
		commands = []
		first_iter = True
		for name, category in self.categories:
			for cog in category:
				for cmd in cog.walk_commands():
					if cmd.hidden:
						continue
					if cmd.parent is None:
						commands.append(f'`{cmd}`')
			self.__setattr__(name, Embed(title=f"{name.title()} commands", description=",".join(commands),
			                             timestamp=datetime.utcnow()))

	@group(name="help", description="The one command where you can see all the commands", invoke_without_command=True)
	async def help_command(self, ctx, icmd: str = None):
		prefix = db.field('SELECT prefix FROM Guild_Settings WHERE guild_id = ?', ctx.guild.id)

		if icmd is None:
			e = Embed(title="**These are the command categories**",
			          description=f"    - My prefix in server **{ctx.guild.name}** is `{prefix}`\n"
			                      f"    - To change my prefix use `{prefix}prefix <new_prefix>`\n\n")

			fields = [
				("General", f"General commands!) \n`{prefix}help general`", True),
				("Gameplay", f"Gameplay commands! \n`{prefix}help gameplay`", True),
				('Misc', f'Misc Commands! \n`{prefix}help misc`', True)
			]

			for name, value, inline in fields:
				e.add_field(name=name, value=value, inline=inline)

			await ctx.send(embed=e)
		elif icmd is not None:
			icmd = icmd.lower()
			cmd: Union[Command, Group]
			for cmd in self.bot.walk_commands():
				name = cmd.name
				aliases = cmd.aliases
				if isinstance(cmd, Command):
					if cmd.parent is not None or cmd.hidden:
						continue
					if name == icmd.lower() or icmd in aliases:
						e = Embed(title=f"{name} Command", description=cmd.description)
						if aliases is not None:
							e.add_field(name="aliases", value=",".join([f'`{alias}`' for alias in aliases]))
						if cmd.brief is not None:
							e.add_field(name='Usage',
							            value=cmd.brief.format(ctx.prefix) if len(
								            cmd.brief.split(',')) == 1 else '\n'.join(
								            cmd.brief.format(prefix).split('******')))

						await ctx.send(embed=e)
						return
			await ctx.send(f"I Checked all the stores in this locality but found no command like `{icmd}`")

	@help_command.command(name="gameplay", description="General Gameplay commands!")
	async def help_command_gameplay(self, ctx):
		await ctx.send(embed=self.__getattribute__("gameplay").set_footer(text=f"Remember to use \"{ctx.prefix}\"."
		                                                                       f" Prefix may vary in servers ping me to know ;)"))

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(str(__name__).split(".")[-1])


def setup(bot):
	bot.add_cog(Help(bot))
