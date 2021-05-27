""" IMPORTS """

import json
import logging
import os
import sys

import discord
import requests
from discord.ext.commands.context import Context
from discord.ext.commands import Bot
from dotenv import load_dotenv

# Imports wiki only if library exists

""" DEFINE BOT """
bot = Bot(
    command_prefix=".",
    intents=discord.Intents.default(),
    case_insensitive=True
)

""" UTILITY FUNCTIONS """
def get_embed(title: str, description: str):
    """ Returns an embed with `title` -str title and `descrption` -str body. """
    return discord.Embed(title=title, description=description, color=0x1D83D4)

def process_text(text: str, author: str):
    # . r = requests.get(download, allow_redirects=True)
    text = "\n".join(text.splitlines())
    if '�' not in text:  # If it's not an image/gif
        truncated = False
        if len(text) > 100000:
            text = text[:99999]
            truncated = True
        req = requests.post('https://bin.bloom.host/documents', data=text)
        key = json.loads(req.content)['key']
        response = "https://bin.bloom.host/" + key
        response += "\nRequested by " + author
        if truncated:
            response += "\n(file was truncated because it was too long.)"
        return response
    else:
        return "ERROR: Received data is image or gif" + "\nRequested by " + author

async def process_potential_paste(ctx: Context, whitelist: tuple):
    if len(ctx.attachments) > 0 and ctx.attachments[0].url.endswith(whitelist):
        text = await discord.Attachment.read(ctx.attachments[0], use_cached=False)
        response = process_text(text.decode('Latin-1'), ctx.author.mention)
        await ctx.channel.send(embed=get_embed("Please use a pasting service", response))
        return True
    return False

async def process_potential_logs(ctx: Context):
    """
    1. Check tests and sum results
    2. Check if passed threshold
    3. Turn message into a pastebin
    4. Send the paste to the channel
    5. Remove original message & terminate loop
    """
    # Check tests and sum results
    result = 0
    for test in pl_definitions.items():
        result += test[1] * ctx.content.count(test[0])
        # Check if passed threshold
        if result >= pl_threshold:
            # Turn message into a pastebin
            response = process_text(ctx.content, ctx.author.mention)

            # Send the paste to the channel
            await ctx.channel.send(embed=get_embed("Here is your pasted code / log file:", response))

            # Terminate loop
            return True

    # Print a message if half the threshold was reached
    if result > pl_threshold / 2:
        print("Half of log/code catching threshold reached {} of {}".format(result, pl_threshold))
    return False



""" BOT EVENTS AND COMMANDS """
@bot.event
async def on_ready():
    # Marks bot as running
    await bot.change_presence(activity=discord.Game('Reading your timing reports'))
    logging.info('Connected to bot: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot fully loaded')
    logging.info('Original creators: https://github.com/Pemigrade/botflop')

@bot.event
async def on_message(ctx: Context):
    # Prevent responding to bot messages
    if ctx.author == bot.user:
        return

    # Exit if message starts with "no kahti" or "no kathi"
    if ctx.content.startswith("no kahti") or ctx.content.startswith("no kathi"):
        return

    # Process pastes
    whitelist = ('.log', '.txt', '.md', '.java', '.py', '.cpp', '.cs', '.yml')
    if await process_potential_paste(ctx, whitelist):
        return

    # Process pasted logs
    if await process_potential_logs(ctx):
        return

    # Process timings
    if ctx.channel.name == ["Optimization","»📩optimalization"]:
        timings = bot.get_cog('Timings')
        await timings.analyze_timings(ctx)

    # Process commands
    await bot.process_commands(ctx)

@bot.command()
async def ping(ctx: Context):
    print(type(ctx))
    await ctx.send(f'Kahti bot ping is {round(bot.latency * 1000)}ms')

@bot.command()
async def invite(ctx: Context):
    await ctx.send('Invite me with this link:\nhttps://discord.com/oauth2/authorize?client_id=801178754772500500'
                   '&permissions=0&scope=bot')

""" SETUP """

# Pasted-log definitions
pl_definitions = {
    "ERROR": 20,
    "INFO": 20,
    "WARN": 20,
    "ERROR]:": 20,
    "INFO]:": 30,
    "WARN]:": 20
}
pl_threshold = 50

# Configure logger
logging.basicConfig(
    filename='console.log',
    level=logging.INFO,
    format='[%(asctime)s %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Load cogs
for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')

# Load token and run bot
load_dotenv()
token = os.getenv('token')
bot.run(token)
