import discord
from discord.ext import commands
import json
import subprocess
import os

auth = None
CONFIG = None

@commands.command()
async def ftp(ctx):
    ip = str(subprocess.check_output(['curl', 'ipinfo.io/ip']))[2:-1]
    msg = f"""To use Pastabot's FTP server, use this info in your FTP client (e.g., Filezilla):
 - Host: {ip}
 - Port: 22
 - Username: files
 - Ask Malapasta for password, or just know it already"""
    await ctx.send(msg)

commands = [ftp]

helps = ["!ftp : get info on using Pastabot's FTP server"]
