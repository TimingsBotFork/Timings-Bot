import os
import discord
import requests
import json
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import aiohttp
import asyncio
import paramiko


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
    if not running_on_panel:
        # Binflop
        if len(message.attachments) > 0:
            if not message.attachments[0].url.endswith(
                    ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image')):
                download = message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(download, allow_redirects=True) as r:

                        # r = requests.get(download, allow_redirects=True)
                        text = await r.text()
                        text = "\n".join(text.splitlines())
                        if '�' not in text:  # If it's not an image/gif
                            truncated = False
                            if len(text) > 100000:
                                text = text[:99999]
                                truncated = True
                            req = requests.post('https://bin.birdflop.com/documents', data=text)
                            key = json.loads(req.content)['key']
                            response = ""
                            response = response + "https://bin.birdflop.com/" + key
                            response = response + "\nRequested by " + message.author.mention
                            if truncated:
                                response = response + "\n(file was truncated because it was too long.)"
                            embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                            embed_var.description = response
                            await message.channel.send(embed=embed_var)
                          

@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')
           
bot.run(token)