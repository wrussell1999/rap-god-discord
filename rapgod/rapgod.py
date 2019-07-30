import discord
from discord.ext import commands
from . import text_to_mp3
from . import lyrics
import threading
from collections import deque
import uuid
import json
import logging

bot = commands.Bot(command_prefix='!')

with open("config/discord.json") as file:
    config = json.load(file)

def main():
    logging.basicConfig(level=logging.INFO)
    token = config['token']
    bot.run(token)

@bot.event
async def on_ready():
    print('Ready!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.command()
async def rap(ctx):
    try:
        word = ctx.message.content.split(' ')[1]
        print(word)
        await ctx.channel.send(word)
    except:
        await ctx.channel.send('Not valid')
