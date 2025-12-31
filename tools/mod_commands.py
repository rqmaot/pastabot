import discord
from discord.ext import commands
import os

from .auth import auth
from . import musicq


muted = []

@commands.command()
async def mute(ctx, userid):
    if await auth.verify(ctx, auth.MODERATOR):
        return
    print(f"muting {userid}")
    already_muted = False
    for entry in muted:
        if entry['id'] == userid and entry['channel'] == ctx.channel.id:
            already_muted = True
            continue
    if not already_muted:
        muted.append({'id': userid, 'channel': ctx.channel.id})

@commands.command()
async def unmute(ctx, userid):
    if await auth.verify(ctx, auth.MODERATOR):
        return
    i = 0
    for entry in muted:
        if entry['id'] == userid and entry['channel'] == ctx.channel.id:
            del muted[i]
            return

async def on_message(msg):
    for user in muted:
        if int(user['id']) == int(msg.author.id) and user['channel'] == msg.channel.id:
            try:
                await msg.delete()
            except Exception as e:
                print(f'Failed to delete: {e}')
            return True
    return False

commands = [mute, unmute]

helps = []
