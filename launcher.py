from atexit import register
from lib.bot import bot
from lib.db import db


@register
def at_exit():
	try:
		bot.scheduler.shutdown()
		db.commit()
		print("stoped execution safely")
	except Exception:
		try:
			db.commit()
			print("db commited but scheduler shutdown failed")
		except Exception:
			print("Couldn't stop execution safely")


bot.run()