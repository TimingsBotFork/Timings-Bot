""" IMPORTS """

import json
import logging
import os
import sys
from difflib import get_close_matches

import discord
import requests
from discord.ext import commands
from discord.ext.commands import has_permissions
from dotenv import load_dotenv

# Imports wiki only if library exists
try:
    if os.path.exists("wiki.py"):
        import wiki as wikilib
except ImportError:
    print("Wiki module import not functioning (wiki.py). Is the file corrupt?")

""" DEFINE BOT """
bot = commands.Bot(
    command_prefix=".",
    intents=discord.Intents.default(),
    case_insensitive=True
)

""" UTILITY FUNCTIONS """


def retrieve_definitions(path):
    """ Retrieves definitions from a json at path `path` - str """
    if not os.path.exists(path):
        print("Could not find {}. Please make sure the file is there.".format(path))
    else:
        with open(path) as file:
            r = json.load(file)
            file.close()
            return r


def get_embed(title, description):
    """ Returns an embed with `title` -str title and `descrption` -str body. """
    return discord.Embed(title=title, description=description, color=0x1D83D4)


def process_text(text, author):
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


async def process_potential_paste(ctx, whitelist):
    if len(ctx.attachments) > 0 and ctx.attachments[0].url.endswith(whitelist):
        text = await discord.Attachment.read(ctx.attachments[0], use_cached=False)
        response = process_text(text.decode('Latin-1'), ctx.author.mention)
        await ctx.channel.send(embed=get_embed("Please use a pasting service", response))
        return True
    return False


async def process_potential_logs(ctx):
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


async def ask_to_ask(ctx):
    if get_close_matches(ctx.content, a2a_definitions, 1, 0.8):
        await ctx.channel.send(embed=get_embed("Please do not ask to ask",
                                               'Just ask your question {} \nhttps://dontasktoask.com/'.format(
                                                   ctx.author.name)))
        await ctx.delete()
        return True
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
    global Wiki
    Wiki = wikilib.Wiki(0)


@bot.event
async def on_message(ctx):
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

    # Check for people asking to ask
    if await ask_to_ask(ctx):
        return

    # Process timings
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(ctx)

    # Process commands
    await bot.process_commands(ctx)


@bot.command()
async def ping(ctx):
    await ctx.send(f'Kahti bot ping is {round(bot.latency * 1000)}ms')


# Only used if the wiki library is present in the folder
@bot.command()
async def wiki(ctx, *args):
    if os.path.exists("wiki.py"):
        await Wiki.wiki(ctx, *args)


@bot.command()
async def reload_modules(ctx, *args):
    """ Reloads all modules specified in `args` """
    res = []
    for module in args:
        if module.endswith(".py"):
            module = module.replace(".py", "")
        try:
            exec('global {}lib'.format(module))
            exec('import {} as {}lib'.format(module, module))
            await ctx.send(embed=get_embed("Reloaded " + module, "Successfully reloaded the {} module".format(module)))
            res.append(module)
        except Exception:
            await ctx.send(
                embed=get_embed("Error while importing " + module, "Did you place the module in the folder?"))
    print("Reloaded modules (" + ", ".join(res) + ")")


@bot.command()
async def reloadw(ctx):
    await reload_modules(ctx, "wiki.py")
    global Wiki
    Wiki = wikilib.Wiki(0)


@bot.command()
async def invite(ctx):
    await ctx.send('Invite me with this link:\nhttps://discord.com/oauth2/authorize?client_id=801178754772500500'
                   '&permissions=0&scope=bot')


@bot.command()
async def packs(ctx):
    await ctx.send(embed=get_embed("Public Packs", '[Overworld](https://github.com/IrisDimensions/overworld)\n['
                                                   'Continents](https://github.com/Astrashh/Continents) (WIP)'))


@bot.command()
async def xyproblem(ctx):
    await ctx.send(embed=get_embed("The XY Problem", 'Do not ask about your attempted solution, '
                                                     'but about your actual problem {} '
                                                     '\nhttps://xyproblem.info/'.format(ctx.author.name)))


@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    logging.info('reacted to ' + url + ' with ' + reaction)


""" SETUP """

# Get ask-to-ask and pasted log/code definitions
a2a_definitions = retrieve_definitions('ask-to-ask.json')["definitions"]
pl_definitions = retrieve_definitions('pasted-logs.json')["definitions"]
pl_threshold = retrieve_definitions('pasted-logs.json')["threshold"]

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

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
