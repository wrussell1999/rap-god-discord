import discord
from discord.ext import commands
from . import text_to_speech
from . import lyrics
import threading
from collections import deque
import uuid
import json
import logging

import asyncio
import time

bot = commands.Bot(command_prefix='!')
songs = lyrics.load_songs()
gen = lyrics.Generator(songs)

clips = {}

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

    print(f'-- Generating rap (theme: {theme_word})...')
    PERF_start = time.time()

    rap_lyrics = gen.generate_lyrics(theme_word)

    PERF_end = time.time()
    print(f'↳ TOTAL LYRICS TIME {PERF_end - PERF_start}')
    print('-- Start audio gen...')
    PERF_start = time.time()

    audio = gen_audio(rap_lyrics)

    PERF_end = time.time()
    print(f'↳ TOTAL AUDIO TIME {PERF_end - PERF_start}')

    voice_channel = bot.get_channel(config['voice_channel_id'])
    try:
        voice_client = await voice_channel.connect()
    except discord.ClientException:
        await ctx.send('Voice channel is already in use')
        return

    await send_audio(audio, voice_client)

def gen_audio(text):
    pcm_buffer = text_to_speech.make_stream(text)
    return discord.PCMAudio(pcm_buffer)

async def send_audio(audio, voice_client):
    voice_client.play(audio)

    # this loop can probably be removed by using the "after=" kwarg
    # of play() that is called when it finishes. however, that seems
    # to be very hard to get to work
    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()
