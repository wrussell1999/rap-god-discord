import json
import logging
import asyncio
import discord
from io import BytesIO

from discord.ext import commands

from queue import Empty

from . import worker

bot = commands.Bot(command_prefix='!')
pool = worker.ContainedPool(thread_count=4)
last_song_cache = {}

with open('config/discord.json') as file:
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
    print('Bot ready!')

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command()
async def rap(ctx):
    words = ctx.message.content.split(' ')

    if (len(words) < 2):
        await ctx.send('Not a valid command.\nTry `!rap <words>`')
        return

    theme_words = ' '.join(words[1:])

    if ctx.message.channel.type == discord.ChannelType.private:
        print(f'- Enqueue \'make_and_encode\' (theme \'{theme_words}\')')
        pool.enqueue('make_and_encode', (theme_words, ctx.message.channel.id))
    else:
        print(f'- Enqueue \'make_track\' (theme \'{theme_words}\')')
        pool.enqueue('make_track', (theme_words, config['voice_channel_id']))

    await ctx.trigger_typing()

@bot.command()
async def save(ctx):
    try:
        stream = last_song_cache[str(config['voice_channel_id'])]
        print(f'- Enqueue \'encode_track\'')
        pool.enqueue('encode_track', (stream, ctx.channel.id))
        await ctx.trigger_typing()
    except KeyError:
        await ctx.send('No previous song found')

async def response_dispatcher():
    while True:
        try:
            completed_task = pool.get_result()
            task_name, result, channel_id = completed_task

            if task_name == 'make_track':
                bot.loop.create_task(play_audio(result, channel_id))
            elif task_name in ['encode_track', 'make_and_encode']:
                bot.loop.create_task(upload_file(result, channel_id))
        except Empty:
            await asyncio.sleep(1)

async def upload_file(stream, channel_id):
    text_channel = bot.get_channel(channel_id)
    print(f'- Dispatch file to \'{text_channel}\'')

    file_object = discord.File(stream, filename='rap.mp3')
    await text_channel.send(file=file_object)

async def play_audio(stream, channel_id):
    voice_channel = bot.get_channel(channel_id)
    print(f'- Dispatch audio to \'{voice_channel}\'')

    last_song_cache[str(channel_id)] = BytesIO(stream.getvalue())

    try:
        voice_client = await voice_channel.connect()
    except discord.ClientException:
        print(f'Cannot connect to channel {voice_channel}')
        return

    if voice_client.is_playing():
        print(f'Channel {voice_channel} is busy')
        return
    else:
        buffer = discord.PCMAudio(stream)
        voice_client.play(buffer)

        # this loop can probably be removed by using the 'after=' kwarg
        # of play() that is called when it finishes. however, that seems
        # to be very hard to get to work with async functions
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()
