import discord
from discord.ext import commands
import json

auth = None
CONFIG = None

def add_to_list(item):
    if not CONFIG.exists("watchlist"): CONFIG.add("watchlist", [])
    CONFIG.get("watchlist").append(item)
    CONFIG.save()

def remove_item(item):
    lines = CONFIG.get("watchlist")
    try:
        i = lines.index(item)
        res = lines[i]
        del lines[i]
        CONFIG.save()
        return res
    except: return False

def remove_index(i):
    try:
        res = CONFIG.get("watchlist")[i - 1]
        del CONFIG.get("watchlist")[i - 1]
        CONFIG.save()
        return res
    except: return False

async def ls(ctx):
    try:
        lines = CONFIG.get("watchlist")
    except: 
        await ctx.send("The watch list is empty")
        return
    if len(lines) == 0:
        await ctx.send("The watch list is empty")
        return
    i = 1
    buf = ''
    for item in lines:
        new_buf = buf + f"\n{i}. {item}" if i > 1 else f"{i}. {item}"
        if len(new_buf) > 2000:
            await ctx.send(buf)
            buf = f"{i}. {item}"
        else: buf = new_buf
        i += 1
    await ctx.send(buf)

@commands.command()
async def watch(ctx, *args):
    print(args)
    item = ' '.join(args).strip()
    if item == '': return await ls(ctx)
    if await auth.verify(ctx, auth.TRUSTED): return
    add_to_list(item)

@commands.command()
async def watched(ctx, *args):
    print(args)
    if await auth.verify(ctx, auth.TRUSTED): return
    item = ' '.join(args).strip()
    by_item = remove_item(item)
    if by_item:
        await ctx.send(f"Removed {by_item} from watch list")
        return
    try:
        by_index = remove_index(int(item))
        if by_index:
            await ctx.send(f"Removed {by_index} from watch list")
            return
        raise Exception('')
    except:
        await ctx.send(f'Could not find "{item}" on watch list. Try !watch to see what\'s on the list')

commands = [watch, watched]

helps = [
        "!watch [optional movie/show name] : display the watch list, or add to it",
        "!watched [watch list name or index] : remove an item from the watch list"
        ]
