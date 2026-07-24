import discord
from discord.ext import commands
import subprocess

class Basics(commands.Cog):
    def __init__(self, app):
        self.app = app
    async def send_dm(self, user_id, msg):
        user = await self.app.bot.fetch_user(int(user_id))
        channel = user.dm_channel
        if channel == None:
            channel = await self.app.bot.create_dm(user)
        await channel.send(msg)
    @commands.Cog.listener()
    async def on_ready(self):
        pasta_ip = self.app.get_ip()
        msg = f'{self.app.bot.user} is online ({pasta_ip})'
        try:
            for admin in self.app.config.get(['auth', 'admin']):
                await self.send_dm(admin['id'], msg)
        except Exception as e: print(f'basics.on_ready: {e}')
        print(msg)
    @commands.command(help='Replies with "pong!"')
    async def ping(self, ctx):
        await ctx.send('pong!')
    @commands.command(help='Replies with Pastabot\'s IP')
    async def ip(self, ctx):
        await ctx.send(self.app.get_ip())
    @commands.command()
    async def say(self, ctx, *args):
        if self.app.auth.check(ctx.author.id) < self.app.auth.MODERATOR: return
        await ctx.send(' '.join(args))
    @commands.command()
    async def dm(self, ctx, user_id, *args):
        if self.app.auth.check(ctx.author.id) < self.app.auth.ADMIN: return
        await self.send_dm(user_id, ' '.join(args))
    @commands.command(help='Replies with the username associated with the given ID')
    async def find(self, ctx, discord_id):
        user = await self.app.bot.fetch_user(int(discord_id))
        await ctx.send(str(user))
    @commands.command(help='Replies with your ID')
    async def whoami(self, ctx):
        await ctx.send(ctx.author.id)
