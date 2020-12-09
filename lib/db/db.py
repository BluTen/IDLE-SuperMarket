import json
from os.path import isfile
from sqlite3 import connect
from contextlib import contextmanager

from apscheduler.triggers.cron import CronTrigger

DB_PATH = "./data/db/database.db"
BOT_SETTINGS_PATH = "./data/db/bot_settings.json"
BUILD_PATH = "./data/db/build.sql"
con = connect(DB_PATH)


# @contextmanager
# def opendb(db_path):
# 	cxn = connect(DB_PATH, check_same_thread=False)
# 	cur = cxn.cursor()
# 	yield cur
# 	cxn.commit()
# 	cur.close()
# 	cxn.close()


def commit():
	with con:
		con.commit()
		print("commited")


def build():
	if isfile(BUILD_PATH):
		with con:
			scriptexec(BUILD_PATH)
	if not isfile(BOT_SETTINGS_PATH):
		with open(BOT_SETTINGS_PATH, 'w') as sf:
			json.dump({'bot_status': 'playing with {users} players', 'debug': True}, sf, indent=2)


def dump(obj):
	with open(BOT_SETTINGS_PATH, 'w') as fp:
		json.dump(obj=obj, fp=fp, indent=4)


def load():
	with open(BOT_SETTINGS_PATH, 'r') as fp:
		return json.load(fp=fp)


def edit(field: str, value):
	data = load()
	if field == 'bot_status' and type(value) is str:
		data[field] = value
		dump(data)
	elif field == 'debug' and type(value) is bool:
		data[field] = value
		dump(data)
	else:
		raise ValueError("Proper values not provided")


def field(command, *values):
	with con:
		cur = con.cursor()
		cur.execute(command, tuple(values))

		if (fetch := cur.fetchone()) is not None:
			return fetch[0]


def record(command, *values):
	with con:
		cur = con.cursor()
		cur.execute(command, tuple(values))

		return cur.fetchone()


def records(command, *values):
	with con:
		cur = con.cursor()
		cur.execute(command, tuple(values))

		return cur.fetchall()


def column(command, *values):
	with con:
		cur = con.cursor()
		cur.execute(command, tuple(values))

		return [item[0] for item in cur.fetchall()]


def execute(command, *values):
	with con:
		cur = con.cursor()
		cur.execute(command, tuple(values))


def multiexec(command, valueset):
	with con:
		cur = con.cursor()
		cur.executemany(command, valueset)


def scriptexec(path):
	with open(path, "r", encoding="utf-8") as script:
		with con:
			cur = con.cursor()
			cur.executescript(script.read())