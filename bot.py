import os
import discord
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import time

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


# Startup Information
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Sea of Thieves'))
    logging.info('Connected to bot: {}'.format(client.user.name))
    logging.info('Bot ID: {}'.format(client.user.id))
    

@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')
           
bot.run(token)