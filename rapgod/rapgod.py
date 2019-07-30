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
    if (len(ctx.message.content) > 1):
        word = ctx.message.content.split(' ')[1]
        print(word)
        # rap_lyrics = gen.generate_lyrics(word)
        # print(rap_lyrics)
        voice_channel = bot.get_channel(config['voice_channel'])
        voice_client = await voice_channel.connect()
        # thread = threading.Thread(target=lambda: send_audio(word, ctx.message.author, voice_channel))
        send_audio(word, ctx.message.author, voice_client)
        
    else:
        await ctx.channel.send('Not valid')

def send_audio(text, user, voice_client):
    user_id = user.id
    filename = f"cache/recordings/{user_id}-{uuid.uuid4()}.mp3"
    filename = text_to_mp3.make_mp3(text, filename)
    if user_id in clips:
        clips[user_id].append(filename)
    else:
        clips[user_id] = deque([filename])
    audio = discord.FFmpegPCMAudio(filename)
    voice_client.play(audio)
    # await voice_client.disconnect()
