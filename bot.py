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
    await bot.change_presence(activity=discord.Game('Fork of the original timings bot'))
    logging.info('Connected to bot: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot fully loaded')
    logging.info('Original creators: https://github.com/Pemigrade/botflop')
    

keyword = "lagg"
@bot.event
async def on_message(message):
      message_text = message.content.strip().lower()
      if keyword in message_text:
          await message.channel.send("If you are lagging, please consider seding a Timings report.")
          await message.channel.send("You can create a timings using the `/timings report` command.")
          
          
          client.command(aliases = ["google","search"],

description = "Will search the internet from a given search term and return the top web result")

u/client.command(aliases = ["google","search"],

description = "Will search the internet from a given search term and return the top web result")

async def Search(ctx,*,query):

searchInput = "https://google.com/search?q="+urllib.parse.quote(query)

res = requests.get(searchInput)

res.raise_for_status()

soup = bs4.BeautifulSoup(res.text, "html.parser")

linkElements = soup.select('div#main > div > div > div > a')

if len(linkElements) == 0:

await ctx.send("Couldn't find any results...")

else:

link = linkElements[0].get("href")

i = 0

while link[0:4] != "/url" or link[14:20] == "google":

i += 1

link = linkElements[i].get("href")

await ctx.send(":desktop: http://google.com"+link)
          
          

@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')
           
bot.run(token)