from discord.ext import commands
import math
import random
import time

from app import Auth, command

class Char(commands.Cog):
    def __init__(self, app):
        self.app = app
        self.CHAR = '320298663161102336'
        self.no_images = False
        self.n_pleading = 0
        self.n_wtf = 0
        self.last_wtf_time = time.time() - 60*60
        random.seed()
    def old_get_wtf_chance(self):
        if self.n_pleading == 0: return 0.5
        t = (self.n_wtf / self.n_pleading)**2
        # t high = low chance next, t low = high chance next
        return 0.1 * t + 0.9 * (1 - t)
    def get_wtf_chance(self):
        t = time.time() - self.last_wtf_time
        return 1 - math.exp(-t / 60)
    @command(auth=Auth.MODERATOR)
    async def charimg(self, ctx):
        self.no_images = not self.no_images
        await ctx.send(f'char can{"not" if self.no_images else ""} send images')
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.app.bot.get_context(msg)
        # pleading face
        if "🥺" in msg.content:
            p = self.get_wtf_chance()
            self.n_pleading += 1
            if random.random() <= p:
                self.n_wtf += 1
                self.last_wtf_time = time.time()
                await ctx.send(file=discord.File('/home/matt/pastabot/wtf.png'))
        if str(msg.author.id) != self.CHAR: return
        # none of that
        if self.no_images and msg.attachments:
            for attachment in msg.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    await msg.delete()
                    await msg.channel.send("none of that")
                    break
