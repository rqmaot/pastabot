import discord
from discord.ext import commands

from . import mp3_util
from . import misc
from .auth import auth

@commands.command()
async def mp3(ctx, link):
    if await auth.verify(ctx, auth.NOAUTH):
        return
    mp3_name, mp3_dir = mp3_util.get_mp3(link)
    if mp3_name == None:
        await ctx.send("Invalid link")
    filepath = f"./{mp3_dir}/{mp3_name}"
    try:
        await ctx.send(file=discord.File(filepath))
    except Exception as e:
        await ctx.send(f"Could not send file: {e}")
        print(f"Error: {e}")
    try:
        await ctx.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")
    try:
        misc.rm(filepath)
        mp3_util.rmdir(mp3_dir)
    except Exception as e:
        print(f"Error deleting: {e}")

commands = [mp3]

helps = [
        "!mp3 [link] : retrieves a song and sends the mp3"
        ]
