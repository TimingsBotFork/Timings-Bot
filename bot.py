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


def get_embed(title, description):
    return discord.Embed(title=title, description=description, color=0x1D83D4)

@bot.event
async def on_message(message):
    # Process pastes
    invalid_extensions = ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image', '.svg')
    await process_potential_paste(message, invalid_extensions)

    # Process pasted logs
    tests = [('[', 5), (']', 5), (':', 3), ('ERROR', 20), ('INFO', 20), ('WARN', 20), ('ERROR]:', 20), ('INFO]:', 30), ('WARN]:', 20)]
    threshold = 50
    await process_potential_logs(message, tests, threshold)

    # Process timings
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    
    # Process commands
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Kahti bot ping is {round(bot.latency * 1000)}ms')

# Only used if the wiki library is present in the folder

async def process_text(text, author):
    # . r = requests.get(download, allow_redirects=True)
    text = "\n".join(text.splitlines())
    if '�' not in text:  # If it's not an image/gif
        truncated = False
        if len(text) > 100000:
            text = text[:99999]
            truncated = True
        req = requests.post(
            'https://bin.bloom.host/documents', data=text)
        key = json.loads(req.content)['key']
        response = "https://bin.bloom.host/" + key
        response += "\nRequested by " + author
        if truncated:
            response += "\n(file was truncated because it was too long.)"
        return response
    else:
        return "ERROR: Received data is image or gif" + "\nRequested by " + author

async def process_potential_paste(message, invalid_extensions):
    if len(message.attachments) > 0 and not message.attachments[0].url.endswith(invalid_extensions):
        download = message.attachments[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(download, allow_redirects=True) as r:
                response = await process_text(unidecode(await r.text()), message.author.mention)
                await message.channel.send(embed=get_embed("Please use a pasting service", response))

async def process_potential_logs(message, tests, threshold):
    """
    1. Check tests and sum results
    2. Check if passed threshold
    3. Turn message into a pastebin
    4. Send the paste to the channel
    5. Remove original message
    """
    # Check tests and sum results
    result = 0
    for test in tests:
        result += test[1] * message.content.count(test[0])
        # Check if passed threshold
        if result >= threshold:
            response = await process_text(message.content, message.author.mention)
            await message.channel.send(embed=get_embed("Here is your pasted code / log file:", response))
            # TODO: Proper message removal function here


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
