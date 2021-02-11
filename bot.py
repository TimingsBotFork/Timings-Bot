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
from unidecode import unidecode

# Imports wiki only if library exists
try:
    if os.path.exists("wiki.py"):
        import wiki as wikilib
except ImportError:
    print("Wiki module import not functioning (wiki.py). Is the file corrupt?")

# Import subprocess
bot = commands.Bot(command_prefix=".", intents=discord.Intents.default(),
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
    # Marks bot as running
    await bot.change_presence(activity=discord.Game('Reading your timing reports'))
    logging.info('Connected to bot: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot fully loaded')
    logging.info('Original creators: https://github.com/Pemigrade/botflop')

@bot.event
async def on_message(message):
    # Binflop
    if len(message.attachments) > 0 and not message.attachments[0].url.endswith(
        ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image', '.svg')):
        download = message.attachments[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(download, allow_redirects=True) as r:

                #. r = requests.get(download, allow_redirects=True)
                text = await r.text()
                text = unidecode(text)
                text = "\n".join(text.splitlines())
                if '�' not in text:  # If it's not an image/gif
                    truncated = False
                    if len(text) > 100000:
                        text = text[:99999]
                        truncated = True
                    req = requests.post('https://bin.bloom.host/documents', data=text)
                    key = json.loads(req.content)['key']
                    response = "https://bin.bloom.host/" + key
                    response += "\nRequested by " + message.author.mention
                    if truncated:
                        response += "\n(file was truncated because it was too long.)"
                    embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                    embed_var.description = response
                    await message.channel.send(embed=embed_var)
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Kahti bot ping is {round(bot.latency * 1000)}ms')

# Only used if the wiki library is present in the folder
@bot.command()
async def wiki(ctx, *args):
    if os.path.exists("wiki.py"):
        await wikilib.wiki(ctx, *args)

@bot.command()
async def invite(ctx):
    await ctx.send('Invite me with this link:\nhttps://discord.com/oauth2/authorize?client_id=801178754772500500&permissions=0&scope=bot')

@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    logging.info('reacted to ' + url + ' with ' + reaction)

for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')

bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
