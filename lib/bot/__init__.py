# Imports of Built In Libraries
from asyncio import sleep
from glob import glob
from datetime import datetime
from os.path import isfile


from pytz import timezone as tz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from discord import Forbidden, HTTPException
from discord import Intents
from discord import Embed, Color
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandOnCooldown, CommandNotFound, NoPrivateMessage
from discord.ext.commands import check, Context, HelpCommand
from discord.ext.commands import when_mentioned_or, command, has_permissions


from ..db import db


OWNER_ID = 430911648736346113

COGS = [path.split("\\")[-1][:-3]for path in glob("./lib/cogs/*.py")]


# noinspection PyUnboundLocalVariable
def get_prefix(bot=None, message=None):
	if message.guild is None:
		for member in bot.get_all_members():
			if member.id == message.author.id:
				prefix = db.field("SELECT prefix FROM Guild_Settings WHERE guild_id = ?", member.guild.id)
				if message.content.startswith(prefix):
					return when_mentioned_or(prefix)(bot, message)
				else: continue
	else:
		return when_mentioned_or(db.field("SELECT prefix FROM Guild_Settings WHERE guild_id = ?", message.guild.id))(
			bot, message)


class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([attr := getattr(self, cog) for cog in COGS])


class Bot(BotBase):
	def __init__(self):
		self.perfect_inv = ""
		self.admin_inv = "https://discord.com/api/oauth2/authorize?client_id=746999103749095464&permissions=8&scope=bot"

		self.TOKEN = 0
		self.debug = db.load()["debug"]
		self.ready = False

		self.guild = None
		self.stdout = None

		self.timezone = tz('America/Chicago')
		self.scheduler = AsyncIOScheduler({'apscheduler.timezone': self.timezone})
		self.jobs = ""

		self.intent = Intents.default()
		self.intent.members = True
		self.intent.typing = False

		self.cogs_ready = Ready()

		super().__init__(command_prefix=get_prefix, owner_id=OWNER_ID, case_insensitive=True, intents=self.intent)

	async def debugging_is_on(self):
		await self.stdout.send("Debugging is on")

	def setup(self):
		for cog in COGS:
			if cog == "help":
				continue
			try:
				self.load_extension(f"lib.cogs.{cog}")
				print(f"{cog} has been loaded")
			except ModuleNotFoundError:
				continue

		# Help should be loaded at last
		self.load_extension(f"lib.cogs.help")
		print(f"help has been loaded")

		print("Setup complete.")

	def run(self):
		self.remove_command("help")

		print("running setup....")
		self.setup()

		with open("./lib/bot/token.0", 'r', encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)
		if ctx.command is not None and ctx.guild is not None:
			if not self.ready:
				await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

			else:
				await self.invoke(ctx)
		elif ctx.command is not None and ctx.guild is None:
			await self.invoke(ctx)

	async def on_connect(self):
		print("bot connected...")

	async def on_disconnect(self):
		print("bot disconnected...")

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(773500093201383474)
			self.stdout = self.get_channel(781865533376299028)
			print("Adding jobs to the scheduler...")
			if self.debug:
				self.scheduler.add_job(self.debugging_is_on, IntervalTrigger(minutes=2), id="debugging_is_on")
			print("Adding jobs done.")
			for index, job in enumerate(self.scheduler.get_jobs()):

				if index is True:
					jobs = ", "
				self.jobs += job.name
			print(f"These are the jobs given: {self.jobs}.")

			print("starting scheduler...")
			self.scheduler.start()
			print("Scheduler started")

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			self.ready = True

			if self.debug:
				await self.stdout.send("Debugging is set to true!")
			elif not self.debug:
				await self.stdout.send("Now Online!")
			print("Bot is ready")

			meta = self.get_cog("Meta")
			await meta.set()

		else:
			print("Bot reconnecting")


bot = Bot()