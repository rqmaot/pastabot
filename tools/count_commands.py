import discord
from discord.ext import commands
import os
import json

auth = None
CONFIG = None

def get_count():
    if CONFIG.exists("count"):
        return CONFIG.get("count")
    return 0

def incr(delta=1, init=1):
    if CONFIG.exists("count"):
        CONFIG.set("count", CONFIG.get("count") + delta)
        CONFIG.save()
        return CONFIG.get("count")
    CONFIG.add("count", init)
    CONFIG.save()
    return init

@commands.command()
async def lils(ctx):
    if await auth.verify(ctx, auth.TRUSTED):
        return
    await ctx.send(get_count())

@commands.command()
async def lilsplus(ctx):
    if await auth.verify(ctx, auth.TRUSTED): 
        return
    try:
        await ctx.send(str(incr()))
    except Exception as e:
        await ctx.send(f"error {e}")

@commands.command()
async def lilsminus(ctx):
    if await auth.verify(ctx, auth.MODERATOR): return
    try: await ctx.send(str(incr(-1)))
    except Exception as e: await ctx.send(f"error {e}")

commands = [lils, lilsplus, lilsminus]
helps = []
