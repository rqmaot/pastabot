import discord
from discord.ext import commands
import os

from .auth import auth

def get_count(filename):
    count = 0
    with open(filename) as f:
        try:
            count = int(f.read())
        except: pass
    return count

def incr(filename):
    count = get_count(filename)
    with open(filename, "w") as f:
        f.write(str(count + 1))
    return count + 1

@commands.command()
async def lils(ctx):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    await ctx.send(get_count("count.txt"))

@commands.command()
async def lilsplus(ctx):
    if await auth.verify(ctx, auth.TRUSTED): 
        return
    try:
        await ctx.send(str(incr("count.txt")))
    except Exception as e:
        await ctx.send(f"error {e}")

commands = [lils, lilsplus]

helps =[]
