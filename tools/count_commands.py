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

def incr():
    if CONFIG.exists("count"):
        CONFIG.set("count", CONFIG.get("count") + 1)
        return CONFIG.get("count")
    CONFIG.add("count", 1)
    return 1

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

commands = [lils, lilsplus]
helps = []
