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
    if (len(words) > 1):
        word = words[1]

        print(f'Generating rap (theme: {word})...')

        rap_lyrics = gen.generate_lyrics(word)
        audio = gen_audio(rap_lyrics)

        print('Connecting voice...')
        voice_channel = bot.get_channel(config['voice_channel_id'])
        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            await ctx.send('Channel in use')
        if not voice_client.is_playing():
            await send_audio(audio, voice_client)
        else:
            await ctx.send('There is currently a rap being played')

    else:
        await ctx.send('Not valid.\nTry `!rap <word>`')


def gen_audio(text):
    print('- Start track gen...')
    PERF_start = time.time()
    pcm_buffer = text_to_speech.make_stream(text)
    PERF_end = time.time()
    print(f'- TOTAL GEN TIME {PERF_end - PERF_start}')

    return discord.PCMAudio(pcm_buffer)

async def send_audio(audio, voice_client):
    print('Start send...')
    PERF_start = time.time()
    await voice_client.play(audio, after=voice_client.disconnect)
    PERF_end = time.time()
    print(f'- TOTAL send {PERF_end - PERF_start}')
