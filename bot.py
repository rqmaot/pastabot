import discord
from discord.ext import commands
import json

from tools import auth

from tools import db_commands
from tools import mp3_commands
from tools import vc_commands
from tools import cipher_commands
from tools import craft_commands

# set up the bot

def get_token():
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        return config["token"]

TOKEN = get_token()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# add commands

@bot.event
async def on_ready():
    msg = f"{bot.user} is online"
    print(msg)

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@bot.command()
async def say(ctx, *, args):
    msg = ""
    for arg in args:
        msg += arg
    await ctx.send(msg)

@bot.command()
async def dm(ctx, user_id, *, args):
    if auth.check(ctx.author.id) < auth.ADMIN:
        return
    msg = ""
    for word in args:
        msg += word
    user = await bot.fetch_user(int(user_id))
    #print(f"sending \"{msg}\" to {user}")
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
        craft_commands.commands)

add_helps(db_commands.helps,
          mp3_commands.helps,
          vc_commands.helps,
          cipher_commands.helps,
          craft_commands.helps)

@bot.command()
async def help(ctx):
    await help_command(ctx, helps)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
