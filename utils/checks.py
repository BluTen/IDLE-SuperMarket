from discord.ext.commands import NoPrivateMessage, check


def guild_only():
	def predicate(ctx):
		if ctx.guild is None:
			raise NoPrivateMessage("This command can't be used in DM's")
		return True

	return check(predicate)