import discord
import asyncio
from discord.ext import commands
from config.bot_config import BotConfig
from config.env import token
from commands.time_management import TimeManagement
from commands.admin import Admin
from utilities.helpers import NotBotOwner

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'I have logged in as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, NotBotOwner):
        await ctx.send('I will not do that for you!')
    else:
        await ctx.send(f"An error occurred: {error}")

async def main():
    async with bot:
        await bot.add_cog(BotConfig(bot))
        await bot.add_cog(TimeManagement(bot))
        await bot.add_cog(Admin(bot))
        await bot.start(token)

asyncio.run(main())
