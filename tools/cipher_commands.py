import discord
from discord.ext import commands

from . import cipher

@commands.command()
async def encrypt(ctx, key, *, args):
    msg = "".join(args)
    ct = cipher.encrypt(msg, key)
    await ctx.send(ct)

@commands.command()
async def decrypt(ctx, key, ct):
    pt = cipher.decrypt(ct, key)
    await ctx.send(pt)

commands = [encrypt, decrypt]
helps = [
        "!encrypt [password] [message] : encrypts a message using AES",
        "!decrypt [password] [ciphertext] : decrypts a message encrypted by pastabot"
        ]
