import json
import discord
from discord.ext import commands
from db import db

def get_token():
    with open("config.json") as config_file:
        config = json.loads(config_file.read())
        return config["token"]

TOKEN = get_token()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

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

bot.run(TOKEN)
