import discord
from discord.ext import commands
from gtts import gTTS
import os

from .auth import auth

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

def generate(speech, msgid, lang='en', tld='co.uk'):
    try:
        os.mkdir('tts')
    except:
        pass
    os.mkdir(f'tts/{msgid}')
    def gen_with_args(use_lang, use_tld):
        try:
            if use_lang and use_tld:
                gTTS(speech, lang=lang, tld=tld).save(f"tts/{msgid}/{msgid}.mp3")
            elif use_lang:
                gTTS(speech, lang=lang, tld='co.uk').save(f"tts/{msgid}/{msgid}.mp3")
            elif use_tld:
                gTTS(speech, lang='en', tld=tld).save(f"tts/{msgid}/{msgid}.mp3")
            else:
                gTTS(speech, lang='en', tld='co.uk').save(f"tts/{msgid}/{msgid}.mp3")
            return (f"{msgid}.mp3", f"tts/{msgid}")
        except: 
            if use_lang and use_tld:
                return gen_with_args(True, False)
            elif use_lang: 
                return gen_with_args(False, True)
            elif use_tld: 
                return gen_with_args(False, False)
            else: 
                return None
    return gen_with_args(True, True)

async def speak(ctx, filename, filedir):
    vc = await _connect(ctx)
    if vc == None:
        await ctx.send("could not connect to voice")
        return
    try:
        sound = discord.FFmpegPCMAudio(f"{filedir}/{filename}", options='-filter:a loudnorm')
        musicq.add(sound, filedir, vc)
        # vc.play(sound)
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

speak_for = []

@commands.command()
async def tts(ctx, userid = None, tld = None, lang = None):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    # get the right args
    if lang is None and userid != None and len(userid) < 8:
        lang = tld
        tld = userid
        userid = None
    if userid is None:
        userid = str(ctx.author.id)
    if tld is None:
        tld = "co.uk"
    if lang is None:
        lang = 'en'
    print(f"setting {userid} {tld} {lang}")
    # remove them if they're already in there
    i = 0
    while i < len(speak_for):
        if speak_for[i]["ctx"].channel.id == ctx.channel.id and speak_for[i]["user"] == userid:
            del speak_for[i]
        else:
            i += 1
    # add them to the list of people to speak for
    speak_for.append({"ctx": ctx, "user": userid, "tld": tld, "lang": lang})

@commands.command()
async def notts(ctx, userid = None):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    if userid == None:
        userid = str(ctx.author.id)
    elif await auth.verify(ctx, auth.MODERATOR):
        return
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
    tld = None
    lang = None
    for user in speak_for:
        if user["ctx"].channel.id == msg.channel.id and user["user"] == str(msg.author.id):
            ctx = user["ctx"]
            tld = user["tld"]
            lang = user["lang"]
            break
    if ctx == None:
        return
    content = msg.content #.lower()
    try:
        (filename, filedir) = generate(content, str(msg.id), lang, tld)
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
