import os
import discord
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import time
import requests
from googlesearch import search 
from db import post_search_data, fetch_search_data
from search import search_main

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
    
    
@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('hi'):
        msg = 'Hey {0.author.mention}'.format(message)
        await message.channel.send(msg)

    if message.content.startswith('!google'):
        query = message.content.split(None, 1)[1]
        author_id = message.author.id
        post_search_data(author_id, query)

        #Test API Data
        #results = ['https://en.wikipedia.org/wiki/Greta_Gerwig', 'https://www.imdb.com/name/nm1950086/', 'https://www.nytimes.com/2019/10/31/movies/greta-gerwig-little-women.html', 'https://www.theguardian.com/film/2018/jan/11/greta-gerwig-regrets-woody-allen-film-i-will-not-work-for-him-again', 'https://www.nytimes.com/2018/01/09/opinion/greta-gerwig-woody-allen-aaron-sorkin.html']
        
        results = search_main(query)
        if results:
            links = ' \n'.join(results)
            print(links)
            msg = 'Hello {}, you searched for {}. The top five results are: \n {}'.format(message.author.mention, query, links)
        else:
            msg = 'Hello {}, you searched for {}. \n Sorry, no matching links found.'.format(message.author.mention, query)
        await message.channel.send(msg)   
           


@bot.event
async def on_message(message):

    timings = bot.get_cog('Timings')

    await timings.analyze_timings(message)
    await bot.process_commands(message)


for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')
           
bot.run(token)