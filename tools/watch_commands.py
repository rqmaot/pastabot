import discord
from discord.ext import commands
import json

from .auth import auth

def get_filename():
    with open('config.json') as config_file:
        config = json.loads(config_file.read())
        return config['watchlist']

def file_is_empty(filename):
    try:
        with open(filename) as f:
            return f.read().strip() == ''
    except:
        return True

def add_to_list(item):
    filename = get_filename()
    pre = '' if file_is_empty(filename) else '\n'
    with open(filename, 'a') as f:
        f.write(pre + item)

def remove_item(item):
    filename = get_filename()
    with open(filename) as f:
        lines = f.read().split('\n')
    try:
        i = lines.index(item)
        res = lines[i]
        del lines[i]
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        return res
    except: return False

def remove_index(i):
    filename = get_filename()
    with open(filename) as f:
        lines = f.read().split('\n')
    try:
        res = lines[i - 1]
        del lines[i - 1]
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        return res
    except: return False

async def ls(ctx):
    try:
        filename = get_filename()
        f = open(filename)
        lines = list(filter(lambda x : x != '', f.read().split('\n')))
        f.close()
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
