import discord
from discord.ext import commands
import random

auth = None
CONFIG = None

@commands.command()
async def rng(ctx, *args):
    n = 10
    try: 
        n = int(args[0])
        assert n > 1
    except: pass
    await ctx.send(f"Picking a random number from 1 to {n}...")
    random.seed()
    x = random.randint(1, n)
    await ctx.send(f"Chose {x}")

@commands.command()
async def choose(ctx, *args):
    random.seed()
    options = ' '.join(args).split(',')
    x = ' '
    try: x = random.choice(options)
    except: pass
    await ctx.send(f"Chose {x.strip()}")

commands = [rng, choose]
helps = [
        "!rng [n] : pick a random number from 1 to n (defaults to 10)",
        "!choose [option 1, option 2, ...] : given a list of choices, pick one",
        ]

