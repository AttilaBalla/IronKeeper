from discord.ext import commands
from utilities.helpers import make_boss_list, require_bot_owner

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @require_bot_owner()
    @commands.command()
    async def kill(self, ctx):
        time_management = ctx.bot.get_cog('TimeManagement')
        time_management.time_keeper.save_timer_state()
        await ctx.send('Shutting down... :(')
        await ctx.bot.close()

    # set brigade that is filtered for when querying brig stats
    @require_bot_owner()
    @commands.command()
    async def set_brigade(self, ctx, brigade):
        bot_config = ctx.bot.get_cog('BotConfig')
        bot_config.brigade = brigade
        await ctx.send(f"Brigade has been set to <@&{bot_config.brigade}>")

    # set boss hunters role ID
    @require_bot_owner()
    @commands.command()
    async def set_boss_hunter_role(self, ctx, role_id):
        bot_config = ctx.bot.get_cog('BotConfig')
        bot_config.boss_hunter_role_id = int(role_id)
        await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! I will notify you when bosses spawn!")

    # set war channel ID
    @require_bot_owner()
    @commands.command()
    async def set_war_channel(self, ctx, channel_id):
        bot_config = ctx.bot.get_cog('BotConfig')
        bot_config.war_channel_id = int(channel_id)
        await ctx.send(f"War-timers channel set to <#{bot_config.war_channel_id}>")

    # set boss channel ID
    @require_bot_owner()
    @commands.command()
    async def set_boss_channel(self, ctx, channel_id):
        bot_config = ctx.bot.get_cog('BotConfig')
        bot_config.boss_channel_id = int(channel_id)
        await ctx.send(f"Boss Hunter channel set to <#{bot_config.boss_channel_id}>")

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