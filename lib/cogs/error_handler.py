import discord
import datetime
import traceback
import sys
from discord.ext import commands


# noinspection PyProtectedMember
class CommandErrorHandler(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""The event triggered when an error is raised while invoking a command.
		Parameters
		------------
		ctx: commands.Context
			The context used for command invocation.
		error: commands.CommandError
			The Exception raised.
		"""
		if isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f'`{ctx.command}` can not be used in Private Messages. \nThe current prefix is based on the server we share')
			except discord.HTTPException:
				pass

		if hasattr(ctx.command, 'on_error'):
			return

		cog = ctx.cog
		if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
			return

		ignored = (commands.CommandNotFound, commands.NotOwner,)
		error = getattr(error, 'original', error)

		if isinstance(error, ignored):
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} has been disabled.')

		elif isinstance(error, commands.BadArgument):
			if ctx.command.qualified_name == 'tag list':
				await ctx.send('I could not find that member. Please try again.')

		else:
			if self.bot.debug:
				e = discord.Embed(title=f"A {type(error).__name__} Error Occurred\nDuring invocation of command `{ctx.command.name}`...",
				                  description=f"```{''.join([line for line in traceback.format_exception(type(error), error, error.__traceback__)])}```",
				                  colour=discord.Colour.dark_red(),
				                  timestamp=ctx.message.created_at).set_footer(text="The above exception occured -->")
				await ctx.send(embed=e)
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

	@commands.Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up(str(__name__).split(".")[-1])


def setup(bot):
	bot.add_cog(CommandErrorHandler(bot))
