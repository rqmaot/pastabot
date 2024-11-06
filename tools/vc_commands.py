import discord
from discord.ext import commands
import json
import os

from . import mp3_util
from . import musicq
from .auth import auth

async def _connect(ctx):
    vc = ctx.voice_client
    if vc == None:
        try:
            vc = await ctx.author.voice.channel.connect()
        except Exception as e:
            return None
    return vc

@commands.command(aliases = ['play'])
async def add(ctx, url):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    vc = await _connect(ctx)
    try:
        mp3, mp3_dir = mp3_util.get_mp3(url)
        filepath = f"./{mp3_dir}/{mp3}"
        sound = discord.FFmpegPCMAudio(filepath, options='-filter:a loudnorm')
        musicq.add(sound, mp3_dir, vc)
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

@commands.command()
async def clear(ctx):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    musicq.clear()
    await ctx.send("cleared the queue")

def get_sound(sound):
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        sounds = config["sounds"]
        prefix = sounds["prefix"]
        keys = sounds["sounds"]
    for k in keys:
        if k.lower() == sound.lower():
            return f"{prefix}/{keys[k]}"
    for f in os.listdir(prefix):
        if sound.lower() in f.lower():
            return f"{prefix}/{f}"
    return None

@commands.command()
async def sound(ctx, *, args):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    sound = ""
    for arg in args:
        sound += arg
    vc = await _connect(ctx)
    if vc == None:
        await ctx.send("could not connect to voice")
        return
    try:
        file = get_sound(sound)
        if file == None:
            await ctx.send("no such sound")
            return
        vc.play(discord.FFmpegPCMAudio(file, options='-filter:a loudnorm'))
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

@commands.command()
async def join_voice(ctx, channel_id = None):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    print("join voice")
    if channel_id == None:
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except Exception as e:
            await channel.send(f"Encountered error: {e}")
    else:
        try:
            channel = bot.get_channel(int(channel_id))
            await channel.connect()
        except Exception as e:
            await channel.send(f"Encountered error: {e}")                                                                                                                                     

@commands.command()
async def leave_voice(ctx):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    print("leave voice")
    await ctx.voice_client.disconnect()

@commands.command()
async def stop(ctx):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    await leave_voice(ctx)
    await join_voice(ctx)

def get_config():
    try:
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
            return config["sounds"]
    except:
        return None

@commands.command()
async def list_sounds(ctx, send_all_flag = None):
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        sounds = config["sounds"]
        prefix = sounds["prefix"]
        keys = sounds["sounds"]
    await ctx.send("sounds:")
    out = ""
    if send_all_flag == None:
        for sound in keys:                                                                                                                                                        
            out += f"{sound}\n"
    else:
        for file in os.listdir(prefix):
            out += f"{file}\n"
    await ctx.send(out)

commands = [add, 
            clear, 
            sound, 
            join_voice, 
            leave_voice, 
            stop, 
            list_sounds]

helps = [
        "!play [link] : adds a song to the queue",
        "!clear : clears the queue",
        "!sound [sound name] : adds a built-in sound to the queue",
        "!join_voice : tells pastabot to join vc",
        "!leave_voice : tells pastabot to leave vc",
        "!stop : stops the currently playing song/sound",
        "!list_sounds : lists available built-in sounds"
        ]
