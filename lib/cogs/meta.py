# Imports of Built In Libraries
import sys
import traceback
from asyncio import TimeoutError
from datetime import datetime, timedelta
from platform import python_version
from time import time

from discord import Activity, ActivityType, Embed, Color
from discord import __version__ as discord_version
from discord.ext.commands import Cog, command
from discord.ext.commands import errors
from discord.ext.commands import has_permissions, is_owner
from psutil import Process, virtual_memory

# Imports of Self-Made Libraries
from utils.checks import guild_only
from ..db import db


# Imports of Downloaded Libraries


class Meta(Cog):
	def __init__(self, bot):
		self.bot = bot

		self._message = db.load()["bot_status"]

	@property
	def message(self):
		return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))

	@message.setter
	def message(self, value):
		if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
			raise ValueError("Invalid activity type.")

		self._message = value

	async def set(self):
		_type, _name = self.message.split(" ", maxsplit=1)

		await self.bot.change_presence(activity=Activity(
			name=_name, type=getattr(ActivityType, _type, ActivityType.playing)
		))

	@is_owner()
	@command(name="setactivity", hidden=True)
	async def set_activity_message(self, ctx, *, text: str):
		try:
			self.message = text
			await self.set()
			db.edit('bot_status', text)
			await ctx.send(
				f"Changed Activity message to `{self.message}` type {self.message.split(' ', maxsplit=1)[0]}")
		except ValueError:
			await ctx.send("Please start the sentence with any of the following words"
			               "`playing, watching, listening, streaming`")

	@is_owner()
	@command(name="debugging", hidden=True)
	async def change_debugging(self, ctx, value: str = None):

		debug_val = db.load()['debug']

		if value is None:
			if debug_val:
				self.bot.debug = False
				db.edit('debug', False)
				self.bot.scheduler.pause_job("debugging_is_on")
				await ctx.send("Debugging is set to `False` any error will not be sent by the bot")
			else:
				self.bot.debug = True
				db.edit('debug', True)
				self.bot.scheduler.resume_job("debugging_is_on")
				await ctx.send("Debugging is set to `True` any error will be sent by the bot")
		elif value.lower() == "true":
			if debug_val:
				await ctx.send("Debugging is already at `True` do you wanna change it to `False`")

				def check(m):
					return (m.content.lower() == 'true' and m.author is ctx.message.author) or (
								m.content.lower() == 'false' and m.author is ctx.message.author)

				try:
					msg = await self.bot.wait_for('message', timeout=10.0, check=check)
					if msg.content.lower() == 'true':
						self.bot.debug = False
						db.edit('debug', False)
						self.bot.scheduler.pause_job("debugging_is_on")
						await ctx.send("Debugging is set to `False` any error will not be sent by the bot")
					elif msg.content.lower() == 'false':
						await ctx.send("OK")
				except TimeoutError:
					pass
			else:
				self.bot.debug = True
				db.edit('debug', True)
				self.bot.scheduler.resume_job("debugging_is_on")
				await ctx.send("Debugging is set to `True` any error will be sent by the bot")
		elif value.lower() in 'false':
			if not debug_val:
				await ctx.send("Debugging is already at `False` do you wanna change it to `True`")

				def check(m):
					return (m.content.lower() == 'true' and m.author is ctx.message.author) or (
								m.content.lower() == 'false' and m.author is ctx.message.author)

				try:
					msg = await self.bot.wait_for('message', timeout=10.0, check=check)
					if msg.content.lower() == 'true':
						self.bot.debug = True
						db.edit('debug', True)
						self.bot.scheduler.resume_job("debugging_is_on")
						await ctx.send("Debugging is set to `True` any error wil be sent by the bot")
					elif msg.content.lower() == 'false':
						await ctx.send("OK")
				except TimeoutError:
					pass
			else:
				self.bot.debug = False
				db.edit('debug', False)
				self.bot.scheduler.pause_job("debugging_is_on")
				await ctx.send("Debugging is set to `False` any error wil not be sent by the bot")

	@command(name="prefix",
	         description="Change my command prefix of this server. You need to have `Manage_Guild` Permission to use this command")
	@has_permissions(manage_guild=True)
	@guild_only()
	async def change_prefix(self, ctx, *, prefix: str = None):
		if prefix is None:
			await ctx.send("You can use this command to change my prefix\n"
			               "**__Note__: You can only have a prefix length of 5 characters and it should not contain spaces**")
		elif " " in prefix:
			await ctx.send(":x:\nYou Can't have a space between.")
		elif len(prefix) > 5:
			await ctx.send(":x:\nPlease change the prefix as it can't be more than 5 characters.")
		else:
			await db.execute("UPDATE Guild_Settings SET prefix = ? WHERE guild_id = ?", prefix, ctx.guild.id)
			await ctx.send(f"**Changed prefix to `{prefix}` successfully!**")

	@change_prefix.error
	async def change_prefix_error(self, ctx, err):
		if isinstance(err, errors.MissingRequiredArgument):
			await ctx.send("I can't have nothing as prefix.")
		elif isinstance(err, errors.MissingPermissions):
			await ctx.send(":x: You need to have `Manage Server` permission for that")
		else:
			if self.bot.debug:
				e = discord.Embed(
					title=f"A {type(error).__name__} Error Occurred\nDuring invocation of command `{ctx.command.name}`...",
					description=f"```{''.join([line for line in traceback.format_exception(type(error), error, error.__traceback__)])}```",
					colour=discord.Colour.dark_red(),
					timestamp=ctx.message.created_at().set_footer(text="The above exception occurred -->"))
				await ctx.send(embed=e)
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	@command(name="ping", description="My latency, **Pong**")
	async def ping(self, ctx):
		start = time()
		message = await ctx.send(f":ping_pong:﻿ Pong! Bot latency: {self.bot.latency * 1000:,.0f} ms.")
		end = time()

		await message.edit(
			content=f":ping_pong:﻿ Pong! Bot latency: {self.bot.latency * 1000:,.0f} ms. Response time: {(end - start) * 1000:,.0f} ms.")

	@command(name="stats", description="Shows all my stats")
	async def show_bot_stats(self, ctx):
		embed = Embed(title="Bot stats",
		              colour=Color.dark_theme(),
		              thumbnail=self.bot.user.avatar_url,
		              timestamp=datetime.utcnow())

		proc = Process()
		with proc.oneshot():
			uptime = timedelta(seconds=time() - proc.create_time())
			uptime = str(uptime).split(".")[0]
			cpu_percent = proc.cpu_percent()
			mem_total = virtual_memory().total / (1024 ** 2)
			mem_of_total = proc.memory_percent()
			mem_usage = mem_total * (mem_of_total / 100)

		fields = [
			("Python version", python_version(), True),
			("discord.py version", discord_version, True),
			("Memory usage", f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)", True),
			("Uptime", uptime, False),
			("Total CPU Usage", f"{cpu_percent}%", False)
		]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)

	@is_owner()
	@command(name="commit", hidden=True)
	async def db_commit(self, ctx):
		db.commit()
		ctx.send("committed the db")

	@is_owner()
	@command(name="load", description="load a cog!", hidden=True)
	async def load_cog(self, ctx, cog: str):
		self.bot.load_extension(f"lib.cogs.{cog}")
		await ctx.send(f"Successfully loaded {cog}")

	@load_cog.error
	async def load_cog_error(self, ctx, err):
		if isinstance(err, errors.MissingRequiredArgument):
			await ctx.send("Which cog to reload?")
		elif isinstance(err.original, errors.ExtensionAlreadyLoaded):
			await ctx.send(f"{err.original.name.split('.')[-1]} Cog is already loaded")
		elif isinstance(err.original, errors.ExtensionNotFound):
			await ctx.send(f"{err.original.name.split('.')[-1]} is not found check the name")
		elif isinstance(err.original, errors.NoEntryPointError):
			await ctx.send(f"{err.original.name.split('.')[-1]} doesnt have a proper setup func")
		elif isinstance(err.original, errors.ExtensionFailed):
			await ctx.send(f"{err.original.name.split('.')[-1]} has a error, loaded {err.original.name.split('.')[-1]} back to the previous state")
		else:
			if self.bot.debug:
				e = Embed(
					title=f"A {type(err).__name__} Error Occurred\nDuring invocation of command `{ctx.command.name}`...",
					description=f"```{''.join([line for line in traceback.format_exception(type(err), err, err.__traceback__)])}```",
					colour=Color.dark_red(),
					timestamp=ctx.message.created_at).set_footer(text="The above exception occurred -->")
				await ctx.send(embed=e)
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(err), err, err.__traceback__, file=sys.stderr)

	@is_owner()
	@command(name="unload", description="unload a cog!", hidden=True)
	async def unload_cog(self, ctx, cog: str):
		try:
			self.bot.unload_extension(f"lib.cogs.{cog}")
			await ctx.send(f"Successfully unloaded {cog}")
		except errors.ExtensionNotLoaded:
			await ctx.send(f"{cog} is already unloaded")

	@is_owner()
	@command(name="reload", description="reload a cog!", hidden=True)
	async def reload_cog(self, ctx, cog: str):
		self.bot.reload_extension(f"lib.cogs.{cog}")
		await ctx.send(f"Successfully reloaded {cog}")

	@reload_cog.error
	async def reload_cog_error(self, ctx, err):
		if isinstance(err, errors.MissingRequiredArgument):
			await ctx.send("Which cog to reload?")
		elif isinstance(err.original, errors.ExtensionNotLoaded):
			try:
				await self.load_cog(ctx, err.original.name.split(".")[-1])
			except errors.ExtensionAlreadyLoaded:
					await ctx.send(f"{err.original.name.split('.')[-1]} Cog is already loaded")
			except errors.ExtensionNotFound:
					await ctx.send(f"{err.original.name.split('.')[-1]} is not found check the name")
			except errors.NoEntryPointError:
					await ctx.send(f"{err.original.name.split('.')[-1]} doesnt have a proper setup func")
			except errors.ExtensionFailed:
					await ctx.send(
						f"{err.original.name} has a error, loaded {err.original.name} back to the previous state")
		elif isinstance(err.original, errors.ExtensionNotFound):
			await ctx.send(f"{err.original.name.split('.')[-1]} is not found check the name")
		elif isinstance(err.original, errors.NoEntryPointError):
			await ctx.send(f"{err.original.name.split('.')[-1]} doesnt have a proper setup func")
		elif isinstance(err.original, errors.ExtensionFailed):
			await ctx.send(
				f"{err.original.name.split('.')[-1]} has a error, loaded {err.original.name.split('.')[-1]} back to the previous state")
		else:
			if self.bot.debug:
				e = Embed(
					title=f"A {type(err).__name__} Error Occurred\nDuring invocation of command `{ctx.command.name}`...",
					description=f"```{''.join([line for line in traceback.format_exception(type(err), err, err.__traceback__)])}```",
					colour=Color.dark_red(),
					timestamp=ctx.message.created_at).set_footer(text="The above exception occurred -->")
				await ctx.send(embed=e)
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(err), err, err.__traceback__, file=sys.stderr)

	@is_owner()
	@command(name="shutdown")
	async def shutdown(self, ctx):
		await ctx.send("Shutting down...")

		db.commit()
		self.bot.scheduler.shutdown()
		await ctx.send("Shutdown successful")
		await self.bot.logout()

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(str(__name__).split(".")[-1])


def setup(bot):
	bot.add_cog(Meta(bot))
