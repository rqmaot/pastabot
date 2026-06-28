import discord
from discord.ext import commands
from gtts import gTTS
import os
import re
import time

auth = None
CONFIG = None

bot = None

char_hates_lily = None

musicq = None
def init(q):
    global musicq
    musicq = q

async def _connect(ctx):
    vc = ctx.voice_client
    if vc == None:
        await musicq.lock.acquire()
        try:
            vc = await ctx.author.voice.channel.connect()
        except Exception as e:
            return None
        finally: musicq.lock.release()
    return vc

async def in_vc(ctx):
    if await auth.verify(ctx, auth.NOAUTH): return
    try:
        vc = await _connect(ctx)
        members = map(lambda member: str(member.id), vc.channel.members)
        # if send: await ctx.send(', '.join(members))
        return list(members)
    except Exception as e:
        # if send: await ctx.send(f"!in_vc error: {e}")
        return []

async def vc_is_just_char_and_lily(ctx):
    CHAR = '320298663161102336'
    LILY = '410075317877735424'
    PASTABOT = '1114245939557842955'
    members = await in_vc(ctx)
    return len(members) == 3 and CHAR in members and LILY in members and PASTABOT in members

def generate(speech, msgid, lang='en', tld='co.uk'):
    try: os.mkdir('tts')
    except: pass
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
        # sound = discord.FFmpegPCMAudio(f"{filedir}/{filename}", options='-filter:a loudnorm')
        async with musicq.lock:
            musicq.add(f"{filedir}/{filename}", dir_to_rm=filedir, vc=vc, track=1)
        # vc.play(sound)
    except Exception as e:
        await ctx.send(f"Encountered error (speak): {e}")

def speak_for(ctx, userid, tld, lang):
    obj = {"channel": str(ctx.channel.id), "user": str(userid), "tld": tld, "lang": lang}
    if CONFIG.exists("tts"):
        CONFIG.get("tts").append(obj)
    else:
        CONFIG.add("tts", [obj])
    CONFIG.save()

def unspeak(ctx, userid):
    if not CONFIG.exists("tts"): return
    records = CONFIG.get("tts")
    save = False
    i = 0
    while i < len(records):
        if int(records[i]["channel"]) == int(ctx.channel.id) and int(records[i]["user"]) == int(userid):
            del records[i]
            save = True
        else: i += 1
    if save: CONFIG.save()

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
    unspeak(ctx, int(userid))
    # add them to the list of people to speak for
    speak_for(ctx, userid, tld, lang)

@commands.command()
async def notts(ctx, userid = None):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    if userid == None:
        userid = str(ctx.author.id)
    elif await auth.verify(ctx, auth.MODERATOR):
        return
    unspeak(ctx, userid)

@commands.command()
async def fixtts(ctx):
    os.system("rm -rf tts")

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

def clean_msg(msg):
    ignore = ["!", "http", ":", "<"]
    keep_capital = ["AI", "VR", "NHS"]
    def map_word(word):
        if True in map(lambda x: word.startswith(x), ignore): return ''
        if word == word.upper() and word not in keep_capital: return word.lower()
        return word
    return ' '.join(map(map_word, re.split('() ', msg)))

async def on_message(msg):
    if not CONFIG.exists("tts"): return
    ctx = None
    tld = None
    lang = None
    for user in CONFIG.get("tts"):
        if int(user["channel"]) == int(msg.channel.id) and int(user["user"]) == int(msg.author.id):
            ctx = await bot.get_context(msg)
            tld = user["tld"]
            lang = user["lang"]
            break
    if ctx == None: return
    if msg.content.startswith("!"): return
    content = clean_msg(msg.content.replace('(', ' ').replace(')', ' ').replace('https', ' https'))
    if content.strip() == '': return
    # special case: char and lily alone, char speaking
    CHAR = '320298663161102336'
    if str(msg.author.id) == CHAR and await vc_is_just_char_and_lily(ctx):
        global char_hates_lily
        if ' '.join(content.split()).lower() == 'i hate lily':
            char_hates_lily = time.time()
            await ctx.send("ok, overridden for an hour")
        elif char_hates_lily is None or time.time() - char_hates_lily > 60 * 60:
            await ctx.send('smh char talk to your girlfriend. can override with "i hate lily"')
            # await ctx.send(f'content="{content}"')
            return
    dbg = f"trying to speak with params: tld={tld} lang={lang}"
    print(dbg)
    try:
        (filename, filedir) = generate(content, str(msg.id), lang, tld)
        await speak(ctx, filename, filedir)
    except: print("Failed to speak")

def buffer_line(line, MAX_MSG_LEN):
    messages = []
    while len(line) > MAX_MSG_LEN:
        messages.append(line[:MAX_MSG_LEN])
        line = line[MAX_MSG_LEN:]
    messages.append(line)
    return list(filter(lambda msg: msg.strip() != '', messages))

def buffer_msg(msg):
    lines = msg.split('\n')
    messages = []
    curr = ''
    MAX_MSG_LEN = 1900
    for line in lines:
        if len(curr) + len(line) >= MAX_MSG_LEN:
            messages.append(curr)
            curr = line
        else:
            curr += "\n" + line
            continue
        if len(line) >= MAX_MSG_LEN:
            messages += buffer_line("\n" + line, MAX_MSG_LEN)
            curr = ""
    messages.append(curr)
    return list(filter(lambda msg: msg.strip() != '', messages))

@commands.command()
async def whotts(ctx):
    if await auth.verify(ctx, auth.MODERATOR): return
    entries = {}
    for entry in CONFIG.get("tts"):
        channel = bot.get_channel(int(entry['channel']))
        if channel is None: channel = int(entry['channel'])
        user = await bot.fetch_user(int(entry['user']))
        if channel in entries: entries[channel].append(user)
        else: entries[channel] = [user]
    out = ""
    for channel in entries:
        try: out += f"\n\n[{channel.name.strip()}]  "
        except: out += f"\n\n<unknown channel [{channel}]>  "
        for user in entries[channel]:
            try: out += f"\n - {user.global_name} ({user.name})  "
            except: out += f"\n - <unknown user [{user}]  "
    if len(out) == 0: await ctx.send("No tts entries")
    else: 
        for msg in buffer_msg(out):
            await ctx.send(msg)

commands = [tts, notts, vtts, fixtts, whotts]

helps = [
        "!tts [user id] [accent] : start saying person's messages in vc",
        "!notts [user id] : stop saying their messages",
        "!vtts : list available tts accents",
        "!fixtts : attempt to fix broken tts"
        ]
