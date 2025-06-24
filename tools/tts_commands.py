import discord
from discord.ext import commands
from gtts import gTTS
import os

from .auth import auth
from . import musicq

async def _connect(ctx):
    vc = ctx.voice_client
    if vc == None:
        try:
            vc = await ctx.author.voice.channel.connect()
        except Exception as e:
            return None
    return vc

def generate(speech, msgid, voice):
    try:
        os.mkdir('tts')
    except:
        pass
    os.mkdir(f'tts/{msgid}')
    try:
        gTTS(speech, lang='en', tld=voice).save(f"tts/{msgid}/{msgid}.mp3")
    except:
        try:
            gTTS(speech, lang='en', tld='co.uk').save(f"tts/{msgid}/{msgid}.mp3")
        except: return None
    return (f"{msgid}.mp3", f'tts/{msgid}')

async def speak(ctx, filename, filedir):
    vc = await _connect(ctx)
    if vc == None:
        await ctx.send("could not connect to voice")
        return
    try:
        sound = discord.FFmpegPCMAudio(f"{filedir}/{filename}", options='-filter:a loudnorm')
        musicq.add(sound, filedir, vc)
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

speak_for = []

@commands.command()
async def tts(ctx, userid = None, voice = None):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    # get the right args
    if voice == None and userid != None and len(userid) < 8:
        voice = userid
        userid = None
    if userid == None:
        userid = str(ctx.author.id)
    if voice == None:
        voice = "co.uk"
    print(f"setting {userid} {voice}")
    # remove them if they're already in there
    i = 0
    while i < len(speak_for):
        if speak_for[i]["ctx"].channel.id == ctx.channel.id and speak_for[i]["user"] == userid:
            del speak_for[i]
        else:
            i += 1
    # add them to the list of people to speak for
    speak_for.append({"ctx": ctx, "user": userid, "voice": voice})

@commands.command()
async def notts(ctx, userid = None):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    if userid == None:
        userid = str(ctx.author.id)
    i = 0
    while i < len(speak_for):
        if speak_for[i]["ctx"].channel.id == ctx.channel.id and speak_for[i]["user"] == userid:
            del speak_for[i]
        else:
            i += 1

@commands.command()
async def fixtts(ctx):
    os.system("rm -r tts")

@commands.command()
async def vtts(ctx):
    msg = """Available tts accents:
Australia - com.au
United Kingdom - co.uk
United States - us
Canada - ca
India - co.in
Ireland ie
South Africa - co.za
Nigeria - com.ng"""
    await ctx.send(msg)

async def on_message(msg):
    ignore = ["!", "http", ":"]
    for i in ignore:
        if msg.content.startswith(i):
            return
    ctx = None
    voice = None
    for user in speak_for:
        if user["ctx"].channel.id == msg.channel.id and user["user"] == str(msg.author.id):
            ctx = user["ctx"]
            voice = user["voice"]
            break
    if ctx == None:
        return
    content = msg.content.lower()
    try:
        (filename, filedir) = generate(content, str(msg.id), voice)
        await speak(ctx, filename, filedir)
    except:
        print("Failed to speak")

commands = [tts, notts, vtts, fixtts]

helps = [
        "!tts [user id] [accent] : start saying person's messages in vc",
        "!notts [user id] : stop saying their messages",
        "!vtts : list available tts accents",
        "!fixtts : attempt to fix broken tts"
        ]
