import discord
from discord.ext import commands
import json
import subprocess
import os

from . import mp3_util
from .auth import auth

def get_params():
    try:
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
            params = config["minecraft"]
            return (params["prefix"], params["jar"], params["java"])
    except Exception as e:
        print(f"Failed to load minecraft params: {e}")
        return None

(prefix, jar, java) = get_params()
java = os.path.abspath(java)

@commands.command()
async def ip(ctx):
    pasta_ip = str(subprocess.check_output(['curl', 'ipinfo.io/ip']))[2:-1]
    await ctx.send(f"pastabot's IP is {pasta_ip}") 

@commands.command()
async def status(ctx):
    processes = str(subprocess.check_output(['ps', '-e']))
    server_running = processes.find('java') != -1
    await ctx.send(f"The minecraft server is {'online' if server_running else 'offline'}")

start_script = f"""session_name="craftsession"
pkill java
tmux kill-session -t $session_name
cmd="{java} -Xmx1024M -Xms1024M -jar {jar} nogui"
tmux new-session -d -s $session_name "$cmd" """

def cmd_script(cmd):
    return f"""cd {prefix}
    session_name="craftsession"
    tmux send-keys -t $session_name "{cmd}" C-m"""

@commands.command()
async def startcraft(ctx):
    if await auth.verify(ctx, auth.MODERATOR):
        return
    global prefix, jar, java
    pwd = os.getcwd()
    os.chdir(prefix)
    print(os.getcwd())
    print(os.listdir())
    print(start_script)
    os.system(start_script)
    os.chdir(pwd)
    await ctx.send("Starting pastacraft")

@commands.command()
async def stopcraft(ctx):
    if await auth.verify(ctx, auth.MODERATOR):
        return
    os.system("pkill java")
    await ctx.send("Stopped pastacraft")

@commands.command()
async def craftcmd(ctx, *, args):
    if await auth.verify(ctx, auth.ADMIN):
        return
    cmd = "".join(args)
    os.system(cmd_script(cmd))

commands = [ip, status, startcraft, stopcraft, craftcmd]

helps = [
        "!ip : responds with pastabot's IP address",
        "!status : check if the pastacraft server is online"
        ]
