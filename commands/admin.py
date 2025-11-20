from discord.ext import commands
from utilities.helpers import make_boss_list, require_bot_owner

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @require_bot_owner()
    @commands.command()
    async def kill(self, ctx):
        await ctx.send('Shutting down... :(')
        exit()

    # set boss hunters role ID
    @require_bot_owner()
    @commands.command()
    async def set_boss_hunter_role(self, ctx, role_id):
        bot_config = ctx.bot.get_cog('BotConfig')
        bot_config.boss_hunter_role_id = int(role_id)
        await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! I will notify you when bosses spawn!")

    # list the available boss data
    @require_bot_owner()
    @commands.command()
    async def boss_list(self, ctx):
        await ctx.send(f"`name - key - spawn time in min`")
        await ctx.send(make_boss_list())

    @require_bot_owner()
    @commands.command()
    async def test(self, ctx, key, *args):
        print(args)
        await ctx.send(args)