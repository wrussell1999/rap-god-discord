import io
import json
import logging
import asyncio
import discord

from discord.ext import commands

from queue import Empty

from . import worker
from rapgod import config

config.load_config()

pool = worker.ContainedPool(thread_count=config.thread_count)
bot = commands.Bot(command_prefix=config.command_prefix)
last_song_cache = {}


def main():
    logging.basicConfig(level=logging.INFO)
    pool.start()
    bot.run(config.token)
    pool.stop()

@bot.event
async def on_ready():
    print('Starting response dispatcher...')
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
        # For DM channels we just send the mp3 file because we can't call them
        print(f'- Enqueue \'make_and_encode\' (theme \'{theme_words}\')')
        pool.enqueue('make_and_encode', (theme_words, ctx.message.channel.id))
    else:
        # For server channels we play in the vocie channel
        print(f'- Enqueue \'make_track\' (theme \'{theme_words}\')')

        try:
            server_id_string = str(ctx.guild.id)
            voice_channel_id = config.voice_channel_map[server_id_string]
        except KeyError:
            await ctx.send('I don\'t know which voice channel to rap in.\n'
                           'A server admin should run the command `!use (name'
                           'of voice channel)` to fix this')
            return

        pool.enqueue('make_track', (theme_words, voice_channel_id))

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


@bot.command()
async def use(ctx):
    user_permissions = ctx.channel.permissions_for(ctx.message.author)

    if not user_permissions.administrator:
        await ctx.send('Only server admins can configure the voice channel')
        return

    words = ctx.message.content.split(' ')

    if len(words) != 2:
        await ctx.send('Usage: `!set (voice channel name)`')
        return

    channel_name = words[1]

    channel_object = discord.utils.get(ctx.guild.voice_channels,
                                       name=channel_name)

    if channel_object is None:
        await ctx.send(f'No voice channel with name \'{channel_name}\' '
                       'found')
        return

    server_id_string = str(ctx.guild.id)
    config.voice_channel_map[server_id_string] = channel_object.id
    config.save_voice_channel_map()

    await ctx.send(f'Voice channel \'{channel_name}\' (id: '
                   f'{channel_object.id}) will be used')

    print(f'Server \'{server_id_string}\' associated voice channel is now '
          f'\'{channel_object.id}\'')


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

    last_song_cache[str(channel_id)] = io.BytesIO(stream.getvalue())

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
