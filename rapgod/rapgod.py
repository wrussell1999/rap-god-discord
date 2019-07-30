import discord
from discord.ext import commands
from . import text_to_mp3
from . import lyrics
import threading
from collections import deque
import uuid
import logging

bot = commands.Bot(command_prefix='!')

def main():
    logging.basicConfig(level=logging.INFO)

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
        word = ctx.message.content.split(' ')[0]
    except:
        ctx.channel.send('Not valid')