import time
import uuid
import json
import logging
import asyncio
import discord
import threading
from collections import deque
from discord.ext import commands

from . import audio
from . import lyrics

bot = commands.Bot(command_prefix='!')
songs = lyrics.load_songs()
gen = lyrics.Generator(songs)
audio.init()

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
    await bot.process_commands(message)

@bot.command()
async def rap(ctx):
    words = ctx.message.content.split(' ')

    if (len(words) != 2):
        await ctx.send('Not a valid command.\nTry `!rap <word>`')
        return

    theme_word = words[1]
    start = time.time()

    print(f'Generating lyrics (theme: {theme_word})...')
    rap_lyrics = gen.generate_lyrics(theme_word)

    print('Generating audio...')
    stream = audio.make_stream(rap_lyrics)

    end = time.time()

    print(f'Done [{end - start}s]')

    voice_channel = bot.get_channel(config['voice_channel_id'])
    try:
        voice_client = await voice_channel.connect()
    except discord.ClientException:
        await ctx.send('Voice channel is already in use')
        return

    await send_audio(stream, voice_client)

async def send_audio(stream, voice_client):
    buffer = discord.PCMAudio(stream)
    voice_client.play(buffer)

    # this loop can probably be removed by using the "after=" kwarg
    # of play() that is called when it finishes. however, that seems
    # to be very hard to get to work
    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()
