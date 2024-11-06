import discord
from discord.ext import commands

from .auth import auth
from .db import db

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

@commands.command()
async def id(ctx, player_id):
    players = db.query_id(player_id)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@commands.command()
async def name(ctx, name):
    players = db.query_name(name)
    res = db.player_list_to_string(players)
    await player_res(ctx, players)

@commands.command()
async def list(ctx, *, args):
    if await auth.verify(ctx, auth.NOAUTH):
        return
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

commands = [id, name, list]

helps = [
        "!id [id] : look up a raot player by their id",
        "!name [name] : look up a raot player by their name",
        ]
