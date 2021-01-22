import os
import discord
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import time
from discord.ext import commands
from googlesearch import search 
import urllib.parse
import requests


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
    await bot.change_presence(activity=discord.Game('Fork of the original timings bot'))
    logging.info('Connected to bot: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot fully loaded')
    logging.info('Original creators: https://github.com/Pemigrade/botflop')
    
@bot.command(helpinfo='Searches the web (or images if typed first)', aliases=['g'])
async def google(ctx, *, searchquery: str):
    searchquerylower = searchquery.lower()
    if searchquerylower.startswith('images '):
        await ctx.send('<https://www.google.com/search?tbm=isch&q={}>'
                       .format(urllib.parse.quote_plus(searchquery[7:])))
    else:
        await ctx.send('<https://www.google.com/search?q={}>'
                       .format(urllib.parse.quote_plus(searchquery)))  
   

@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')
           
bot.run(token)