import json
import discord
from discord.ext import commands
import yt_dlp
import os
import subprocess

from db import db
from auth import auth
import misc
import mp3_util
import musicq

def get_token():
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        return config["token"]

TOKEN = get_token()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def player_res(ctx, player_list):
    if len(player_list) == 0:
        return await ctx.send("No data")
    str_list = []
    cum_len = []
    start = 0
    for i in range(len(player_list)):
        if i > 0 and cum_len[i - 1] >= 1500:
            cur = ""
            for x in range(start, i - 1):
                cur += str_list[x] + "\n"
            try:
                await ctx.send(cur)
            except:
                i1 = player_list[i - 1]
                await ctx.send(f'--------------------------------------\n{i1["NAME"][-1]}   [{i1["ID"]}]')
                buf = ""
                for n in range(len(i1["NAME"])):
                    if len(buf) >= 1500:
                        await ctx.send(buf)
                        buf = ""
                    buf += i1["NAME"][n]
                    if n + 1 < len(i1["NAME"]):
                        buf += ", "
                await ctx.send(buf)
            start = i - 1
            cum_len[i - 1] = len(str_list[i - 1])
        str_list.append(db.player_string(player_list[i]))
        cum_len.append(len(str_list[i]))
        if i > 0:
            cum_len[i] += cum_len[i - 1]
    cur = ""
    to_finish = len(str_list)
    for i in range(start, len(str_list)):
        if cum_len[i] < 1500:
            cur += str_list[i] + "\n"
        else:
            to_finish = i
            break
    await ctx.send(cur)
    for i in range(to_finish, len(str_list)):
        await ctx.send(str_list[i])


@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.command()
async def ping(ctx):
    await ctx.send('pong!')

@bot.command()
async def id(ctx, player_id):
    players = db.query_id(player_id)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@bot.command()
async def name(ctx, name):
    players = db.query_name(name)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@bot.command()
async def list(ctx, *, args):
    liststr = ""
    for arg in args:
        liststr += f"{arg}"
    list_response = db.parse_list(liststr)
    for i in range(len(list_response)):
        (name, uuid, discord_id, query) = list_response[i]
        try:
            user = await bot.fetch_user(int(discord_id))
        except:
            user = {"id": discord_id}
        list_response[i] = (name, uuid, user, query)
    messages = db.list_messages(list_response)
    for msg in messages:
        await ctx.send(msg)

@bot.command()
async def mp3(ctx, link):
    mp3_name, mp3_dir = mp3_util.get_mp3(link)
    if mp3_name == None:
        await ctx.send("Invalid link")
    filepath = f"./{mp3_dir}/{mp3_name}"
    try:
        await ctx.send(file=discord.File(filepath))
    except Exception as e:
        print(f"Error: {e}")
    try:
        await ctx.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
    try:
        misc.rm(filepath)
        mp3_util.rmdir(mp3_dir)
    except Exception as e: 
        print(f"Error deleting: {e}")

async def _connect(ctx):
    vc = ctx.voice_client
    if vc == None:
        try:
            vc = await ctx.author.voice.channel.connect()
        except Exception as e:
            return None
    return vc

@bot.command(aliases = ['play'])
async def add(ctx, url):
    vc = await _connect(ctx)
    try:
        mp3, mp3_dir = mp3_util.get_mp3(url)
        filepath = f"./{mp3_dir}/{mp3}"
        sound = discord.FFmpegPCMAudio(filepath, options='-filter:a loudnorm')
        musicq.add(sound, mp3_dir, vc)
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

@bot.command()
async def clear(ctx):
    musicq.clear()
    await ctx.send("cleared the queue")

@bot.command()
async def sound(ctx, *, args):
    sound = ""
    for arg in args:
        sound += arg
    if auth.check(ctx.author.id) < auth.TRUSTED:
        await ctx.send("you are not authorized to play sounds")
        return
    vc = await _connect(ctx)
    if vc == None:
        await ctx.send("could not connect to voice")
        return
    try:
        file = misc.get_sound(sound)
        if file == None:
            await ctx.send("no such sound")
            return
        vc.play(discord.FFmpegPCMAudio(file, options='-filter:a loudnorm'))
    except Exception as e:
        await ctx.send(f"Encountered error: {e}")

@bot.command()
async def stop(ctx):
    await leave_voice(ctx)
    await join_voice(ctx)

@bot.command()
async def dm(ctx, user_id, *, args):
    if auth.check(ctx.author.id) < auth.ADMIN:
        return
    msg = ""
    for word in args:
        msg += word
    user = await bot.fetch_user(int(user_id))
    #printf(f"sending \"{msg}\" to {user}")
    channel = user.dm_channel
    if channel == None:
        channel = await bot.create_dm(user)
    await channel.send(msg)

@bot.command()
async def find(ctx, discord_id):
    user = await bot.fetch_user(int(discord_id))
    await ctx.send(str(user))

@bot.command()
async def whoami(ctx):
    await ctx.send(ctx.author.id)

@bot.command()
async def help(ctx):
    msg = "Available commands: !id, !name, !ping, !list, !mp3, !help\n"
    msg += "- `!id ID_HERE` : search a player by their id (you can find it by running list in the raot console)\n"
    msg += "- `!name NAME_HERE` : search a player by their name. case insensitive\n"
    msg += "- `!ping` : responds with \"pong!\", useful for checking if the bot is online\n"
    msg += "- `!list PASTE_LIST_OUTPUT` : paste the output of the list command to query every player in a lobby\n"
    msg += "- `!mp3 LINK_HERE` : get an mp3 from a youtube video\n"
    msg += "- `!help` : display this message\n"
    await ctx.send(msg)

@bot.command()
async def ip(ctx):
    pasta_ip = str(subprocess.check_output(['curl', 'ipinfo.io/ip']))[2:-1]
    await ctx.send(f"The pastacraft server IP is {pasta_ip}") 

@bot.command()
async def startcraft(ctx):
    if auth.check(ctx.author.id) < auth.MODERATOR:
        return
    os.system("sh /root/craft/run.sh")
    await ctx.send("Starting pastacraft")

@bot.command()
async def deleteThatShit(ctx, msg_id):
    if auth.check(ctx.author.id) < auth.MODERATOR:
        return
    msg = await ctx.fetch_message(msg_id)
    try:
        await ctx.message.delete()
        await msg.delete()
        await ctx.send("deleted that shit")
    except Exception as e:
        print(e)
        await ctx.send("i can't delete that shit")

@bot.command()
async def deleteThatShitQuietly(ctx, msg_id):
    if auth.check(ctx.author.id) < auth.MODERATOR:
        return
    msg = await ctx.fetch_message(msg_id)
    try:
        await ctx.message.delete()
        await msg.delete()
    except Exception as e:
        print(e)

@bot.command()
async def deleteAllThatShit(ctx, *, args):
    if auth.check(ctx.author.id) < auth.MODERATOR:
        return
    for msgid in args:
        msg = await ctx.fetch_message(msgid)
        if msg == None:
            continue
        try:
            await msg.delete()
        except:
            pass
    try:
        await ctx.message.delete()
        await ctx.send("deleted all that shit")
    except Exception as e:
        print(e)
        await ctx.send("couldn't delete that shit")

@bot.command()
async def say(ctx, *, args):
    msg = ""
    for arg in args:
        msg += arg
    await ctx.send(msg)

@bot.command()
async def join_voice(ctx):
    print("join voice")
    channel = ctx.author.voice.channel
    await channel.connect()
@bot.command()
async def leave_voice(ctx):
    print("leave voice")
    await ctx.voice_client.disconnect()

def get_config():
    try:
        with open("config.json") as config_file:
            return json.loads(config_file.read())
    except:
        return None

def get_sounds_json(config):
    try:
        with open(config["sounds"]) as sounds_file:
            return json.loads(sounds_file.read())
    except:
        return None

@bot.command()
async def list_sounds(ctx, files = None):
    sounds = get_sounds_json(get_config())
    if sounds == None:
        await ctx.send("no sounds")
        return
    await ctx.send("sounds:")
    out = ""
    if files == None:
        for sound in sounds["sounds"]:
            out += f"{sound}\n"
    else:
        for file in os.listdir(sounds["prefix"]):
            out += f"{file}\n"
    await ctx.send(out)

#@bot.event
#async def on_message(message):
#    if message.author == bot.user or message.content.startswith(bot.command_prefix):
#        return
#    print(f"[{message.author}:{message.author.id}] {message.content}")

class App:
    def __init__(self):
        self.bot = bot
    def run(self):
        self.bot.run(TOKEN)

app = App()

if __name__ == "__main__":
    bot.run(TOKEN)
