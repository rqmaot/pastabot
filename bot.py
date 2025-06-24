import discord
from discord.ext import commands
import json
import os

from tools.auth import auth

from tools import db_commands
from tools import mp3_commands
from tools import vc_commands
from tools import cipher_commands
from tools import craft_commands
from tools import tts_commands
from tools import watch_commands
from tools import mod_commands

# set up the bot

def initialize():
    global TOKEN
    global CONFIG
    with open("config.json") as config_file:
        CONFIG = json.loads(config_file.read())
        TOKEN = CONFIG["token"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# add commands

async def send_dm(user_id, msg):
    user = await bot.fetch_user(int(user_id))
    #print(f"sending \"{msg}\" to {user}")
    channel = user.dm_channel
    if channel == None:
        channel = await bot.create_dm(user)
    await channel.send(msg)

@bot.event
async def on_ready():
    msg = f"{bot.user} is online"
    try:
        for admin in CONFIG["auth"]["admin"]:
            await send_dm(admin["id"], msg)
    except: pass
    print(msg)

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if await auth.verify(msg, auth.NOAUTH):
        return
    try:
        await bot.process_commands(msg)
        await tts_commands.on_message(msg)
        await mod_commands.on_message(msg)
    except Exception as e:
        await msg.channel.send(f"Encountered error: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def say(ctx, *, args):
    msg = "".join(args)
    await ctx.send(msg)

@bot.command()
async def dm(ctx, user_id, *, args):
    if auth.check(ctx.author.id) < auth.ADMIN:
        return
    msg = "".join(args)
    await send_dm(user_id, msg)

@bot.command()
async def find(ctx, discord_id):
    user = await bot.fetch_user(int(discord_id))
    await ctx.send(str(user))

@bot.command()
async def whoami(ctx):
    await ctx.send(ctx.author.id)

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
async def deleteAllThatShit(ctx, *args):
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

def add(commands):
    for cmd in commands:
        bot.add_command(cmd)

def add_all(*commandses):
    for cmds in commandses:
        add(cmds)

def add_to_helps(helps, more):
    for h in more:
        helps.append(h)

def add_helps(*args):
    for h in args:
        add_to_helps(helps, h)

async def help_command(ctx, helps):
    out = ""
    for h in helps:
        out += f" - {h}\n"
    await ctx.send(out)

helps = [
        "!ping : replies \"pong!\""
        ]

add_all(db_commands.commands,
        mp3_commands.commands,
        vc_commands.commands,
        cipher_commands.commands,
        craft_commands.commands,
        tts_commands.commands,
        watch_commands.commands,
        mod_commands.commands)

add_helps(db_commands.helps,
          mp3_commands.helps,
          vc_commands.helps,
          cipher_commands.helps,
          craft_commands.helps,
          tts_commands.helps,
          watch_commands.helps)

@bot.command()
async def help(ctx):
    await help_command(ctx, helps)

@bot.command()
async def reset(ctx):
    if auth.check(ctx.author.id) < auth.TRUSTED:
        return
    oscmd("sh /root/run.sh")

helps.append("!reset : reboot the bot")

def oscmd(cmd):
    try:
        os.system(cmd)
    except:
        pass

def main():
    oscmd("rm -r tts")
    initialize()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
