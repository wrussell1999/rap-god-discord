import time
import uuid
import json
import logging
import asyncio
import discord
import threading
from collections import deque
from discord.ext import commands

from . import worker

bot = commands.Bot(command_prefix='!')
pool = worker.WorkerPool(thread_count=4)

with open("config/discord.json") as file:
    config = json.load(file)

def main():
    logging.basicConfig(level=logging.INFO)
    token = config['token']
    pool.start()
    bot.run(token)

@bot.event
async def on_ready():
    print('Starting response dispatcher')
    bot.loop.create_task(response_dispatcher())
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

    print(f'Enqueue job (theme \'{theme_word}\')')
    pool.enqueue(theme_word, config['voice_channel_id'])

async def response_dispatcher():
    while True:
        prepared_track = pool.get_result()
        if prepared_track is None:
            await asyncio.sleep(1)
        else:
            stream, channel_id = prepared_track
            await send_response(stream, channel_id)

async def send_response(stream, channel_id):
    print(f'Disptch {stream} to {channel_id}')
    voice_channel = bot.get_channel(channel_id)

    try:
        voice_client = await voice_channel.connect()
    except discord.ClientException:
        print(f'Cannot connect to channel {channel_id}')
        return

    if not voice_client.is_playing():
        await send_audio(stream, voice_client)
    else:
        print(f'Channel {channel_id} is busy')
        return

async def send_audio(stream, voice_client):
    buffer = discord.PCMAudio(stream)
    voice_client.play(buffer, after=voice_client.disconnect)

    # this loop can probably be removed by using the "after=" kwarg
    # of play() that is called when it finishes. however, that seems
    # to be very hard to get to work
    # while voice_client.is_playing():
    #     await asyncio.sleep(1)
    #
    # await voice_client.disconnect()
