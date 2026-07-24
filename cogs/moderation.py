from discord.ext import commands
import os
import subprocess
import sys
import time

class Moderation(commands.Cog):
    def __init__(self, app):
        self.app = app
        self.muted = {}
    @commands.command()
    async def delete(self, ctx, *msg_ids):
        if await self.app.auth.verify(ctx, self.app.auth.MODERATOR): return
        for msg_id in msg_ids:
            try:
                msg = await ctx.fetch_message(msg_id)
                await ctx.message.delete()
                await msg.delete()
            except Exception as e:
                await ctx.send(f'moderation.delete: {e}')
    @commands.command(help='Reset pastabot')
    async def reset(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        await ctx.send('Resetting...')
        cmd = ['python3'] + sys.argv
        try: os.execv(sys.executable, cmd)
        except Exception as e: await ctx.send(f'moderation.reset: {e}')
    @commands.command()
    async def mute(self, ctx, user_id):
        if await self.app.auth.verify(ctx, self.app.auth.MODERATOR): return
        if not self.app.config.exists('muted'): self.app.config.set('muted', {})
        try:
            user_id = str(user_id)
            if user_id in self.app.config.get('muted'): 
                self.app.config.get('muted')[user_id][str(ctx.channel.id)] = time.time()
            else: self.app.config.get('muted')[user_id] = {str(ctx.channel.id): time.time()}
            self.app.config.save()
        except Exception as e:
            await ctx.send(f'moderation.mute: {e}')
    @commands.command()
    async def unmute(self, ctx, user_id):
        if await self.app.auth.verify(ctx, self.app.auth.MODERATOR): return
        if not self.app.config.exists('muted'): return
        if user_id not in self.app.config.get('muted'): return
        if str(ctx.channel.id) not in self.app.config.get('muted')[user_id]: return
        del self.app.config.get('muted')[user_id][str(ctx.channel.id)]
        self.app.config.save()
    def is_muted(self, user_id, channel_id):
        if not self.app.config.exists('muted'): return False
        if user_id not in self.app.config.get('muted'): return False
        if channel_id not in self.app.config.get('muted')[user_id]: return False
        return time.time() - self.app.config.get('muted')[user_id][channel_id] < 10*60
    @commands.Cog.listener()
    async def on_message(self, msg):
        if self.is_muted(str(msg.author.id), str(msg.channel.id)):
            try: await msg.delete()
            except Exception as e: print(f'moderation.on_message: {e}')

