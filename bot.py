import os
import discord
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv

# import subprocess

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), chunk_guilds_at_startup=True,
                   case_insensitive=True)
load_dotenv()

token = os.getenv('token')

logging.basicConfig(filename='console.log',
                    level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


@bot.event
async def on_ready():
    logging.info('I am running.')


@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


@updater.before_loop
async def before_updater():
    await bot.wait_until_ready()


if running_on_panel:
    for file_name in os.listdir('./cogs'):
        if file_name.endswith('_panel.py'):
            bot.load_extension(f'cogs.{file_name[:-3]}')
else:
    for file_name in os.listdir('./cogs'):
        if file_name.endswith('_public.py'):
            bot.load_extension(f'cogs.{file_name[:-3]}')

if running_on_panel:
    print("running on panel, starting loops")
    updater.start()
    linking_updater = bot.get_cog('Linking_updater')
    linking_updater.linking_updater.start()
           
bot.run(token)