import discord
from discord.ext import commands
import json
import os
from pathlib import Path

from . import mp3_util

auth = None
CONFIG = None

musicq = None
def init(q):
    global musicq
    musicq = q

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
        # sound = discord.FFmpegPCMAudio(filepath, options='-filter:a loudnorm')
        # musicq.add(sound, mp3_dir, vc)
        musicq.add(filepath, dir_to_rm=mp3_dir, vc=vc, track=2)
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

@commands.command()
async def clear(ctx):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    musicq.clear()
    await ctx.send("cleared the queue")

def get_sound(sound, root=None):
    sounds = CONFIG.get("sounds")
    if root is None: root = sounds["prefix"]
    parts = sound.split('/')
    subdirs = []
    for f in sorted(os.listdir(root)):
        subpath = os.path.join(root, f)
        if Path(subpath).is_dir():
            if len(parts) > 1 and parts[0].lower() in f.lower():
                sub = get_sound("/".join(parts[1:]), subpath)
                if sub is not None: return sub
            subdirs.append(subpath)
            continue
        if sound.lower() in f.lower():
            return subpath
    for subdir in subdirs:
        sub = get_sound(sound, subdir)
        if sub is not None: return sub
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
        # vc.play(discord.FFmpegPCMAudio(file, options='-filter:a loudnorm'))
        # musicq.add(discord.FFmpegPCMAudio(file, options='-filter:a loudnorm'), None, vc)
        musicq.add(file, vc=vc)
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
async def stop(ctx, *args):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    # await leave_voice(ctx)
    # await join_voice(ctx)
    try: track = int(args[0])
    except: track = None
    try:
        vc = ctx.guild.voice_client
        # if vc and vc.is_playing():
        #     vc.stop()
        musicq.stop(vc, track)
    except Exception as e:
        await ctx.send(f"Failed: {e}")

def get_config():
    try:
        return CONFIG.get("sounds")
    except:
        return None

def get_list(query, path=None):
    root = CONFIG.get("sounds")["prefix"]
    if path is None: path = root
    parts = query.split('/')
    subdirs = []
    for f in sorted(os.listdir(path)):
        subpath = os.path.join(path, f)
        if not Path(subpath).is_dir(): continue
        subdirs.append(subpath)
        if parts[0].lower() not in f.lower(): continue
        if len(parts) > 1:
            sub = get_list("/".join(parts[1:]), subpath)
            if sub is not None: return sub
            continue
        files = []
        dirs = []
        for f1 in sorted(os.listdir(subpath)):
            subsubpath = os.path.join(subpath, f1)
            name = subsubpath[(len(root) + 1):]
            if Path(subsubpath).is_dir(): dirs.append(name + "/")
            else: files.append(name)
        return "\n".join(files + dirs)
    for subdir in subdirs:
        sub = get_list(query, subdir)
        if sub is not None: return sub
    return None

@commands.command()
async def list_sounds(ctx, query=None):
    if query is None: 
        await ctx.send("sounds:")
        files = []
        dirs = []
        root = CONFIG.get("sounds")["prefix"]
        for path in sorted(os.listdir(root)):
            if Path(os.path.join(root, path)).is_dir(): dirs.append(path + "/")
            else: files.append(path)
        await ctx.send("\n".join(files + dirs))
        return
    res = get_list(query)
    if res is None:
        await ctx.send("No sounds found. Try with no arguments for root list")
    await ctx.send(f"{query} sounds:\n{res}")

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
