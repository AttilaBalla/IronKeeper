import os
from dotenv import load_dotenv
import discord
import asyncio
from discord.ext import commands
from config.bot_config import BotConfig
from commands.time_management import TimeManagement
from commands.admin import Admin
from utilities.helpers import NotBotOwner

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
timers_csv = os.getenv('TIMERS_CSV_PATH')
war_channel_id = os.getenv('WAR_CHANNEL_ID')
boss_channel_id = os.getenv('BOSS_CHANNEL_ID')

@bot.event
async def on_ready():
    print(f'I have logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, NotBotOwner):
        await ctx.send('I will not do that for you!')
    else:
        await ctx.send(f"An error occurred: {error}")

def setup_bot_config():
    bot_config = BotConfig(bot)
    bot_config.war_channel_id = war_channel_id
    bot_config.boss_channel_id = boss_channel_id

    return bot_config

def setup_time_management():
    time_management = TimeManagement(bot)
    # set persistence path on the TimeKeeper and attempt to load existing timers
    time_management.time_keeper.persistence_path = timers_csv
    try:
        loaded = time_management.time_keeper.load_from_csv()
        if loaded:
            print(f'Loaded {loaded} timers from {timers_csv}')
    except Exception as error:
        print(f'An error occurred when attempting to load timers from csv: {error}')

    return time_management


async def main():
    async with bot:
        await bot.add_cog(setup_bot_config())
        await bot.add_cog(setup_time_management())
        await bot.add_cog(Admin(bot))
        await bot.start(token)

asyncio.run(main())
