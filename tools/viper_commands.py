import discord
from discord.ext import commands
import json
import subprocess
import os

from .auth import auth

@commands.command()
async def ls(ctx):
    files = subprocess.check_output(['ls', '/home/viper']).decode()
    await ctx.send(files)

@commands.command()
async def scp(ctx):
    ip = str(subprocess.check_output(['curl', 'ipinfo.io/ip']))[2:-1]
    await ctx.send(f"To get FILENAME: `scp viper@{ip}:FILENAME .`\nTo send FILENAME: `scp FILENAME viper@{ip}:.`")

commands = [ls, scp]

helps = [
        "!ls : see the files you can get from pastabot",
        "!scp : see how to use the scp command to transfer files to/from pastabot"
        ]
