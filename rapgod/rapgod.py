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
    words = ctx.message.content.split(' ')
    if (len(words) > 1):
        word = words[1]
        print(word)
        rap_lyrics = gen.generate_lyrics(word)
        voice_channel = bot.get_channel(config['voice_channel_id'])
        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            await ctx.send('Channel in use')
        if not voice_client.is_playing():
            send_audio(rap_lyrics, ctx.message.author, voice_client)
        else:
            await ctx.send('There is currently a rap being played')  
        
    else:
        await ctx.send('Not valid.\nTry `!rap <word>`')

def send_audio(text, user, voice_client):
    user_id = user.id
    filename = f"cache/recordings/{user_id}-{uuid.uuid4()}.mp3"
    filename = text_to_mp3.make_mp3(text, filename)
    audio = discord.FFmpegPCMAudio(filename)
    voice_client.play(audio)
