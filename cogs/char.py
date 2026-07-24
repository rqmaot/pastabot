import discord
from discord.ext import commands
import random
import time

class Char(commands.Cog):
    def __init__(self, app):
        self.app = app
        self.notified_deafened = {}
        self.CHAR = '320298663161102336'
        self.LILY = '410075317877735424'
        self.PASTABOT = '1114245939557842955'
        self.no_images = False
    async def vc_is_just_char_and_lily(self, channel):
        if channel is None: return False
        members = list(map(lambda member: str(member.id), channel.members))
        if self.CHAR not in members: return False
        if self.LILY not in members: return False
        for member in members:
            if member not in [self.CHAR, self.LILY, self.PASTABOT]: return False
        return True
    def enable_smh_mode(self):
        if not self.app.config.exists('tts'): return
        if self.app.config.exists('smh') and self.app.config.get('smh')['enabled']:
            return
        if not self.app.config.exists('smh'): 
            self.app.config.add('smh', {'time': 0})
        self.app.config.get('smh')['enabled'] = True
        self.app.config.get('smh')['backup'] = {}
        if self.CHAR not in self.app.config.get('tts'): return
        self.app.config.get('smh')['backup'] = self.app.config.get('tts')[self.CHAR]
        del self.app.config.get('tts')[self.CHAR]
        self.app.config.save()
    def disable_smh_mode(self):
        if not self.app.config.exists('smh') or not self.app.config.get('smh')['enabled']: 
            return
        if not self.app.config.exists('tts'): self.app.config.add('tts', {})
        self.app.config.get('tts')[self.CHAR] = self.app.config.get('smh')['backup']
        self.app.config.get('smh')['enabled'] = False
        self.app.config.get('smh')['backup'] = {}
        self.app.config.save()
    @commands.Cog.listener()
    async def on_ready(self):
        self.disable_smh_mode()
    async def notify_deafened(self, channel):
        cid = int(channel.id)
        if cid in self.notified_deafened and time.time() - self.notified_deafened[cid] < 5:
            return
        self.notified_deafened[cid] = time.time()
        await channel.send('everyone is deafened until char mutes')
    async def deafen_for_char(self, channel):
        if channel is None: return
        char_unmuted = False
        for member in channel.members:
            if str(member.id) == self.CHAR:
                char_unmuted = not (member.voice.self_mute or member.voice.mute)
                break
        did_edit = False
        for member in channel.members:
            deafen = char_unmuted and str(member.id) != self.CHAR and str(member.id) != self.LILY
            if member.voice.deaf != deafen:
                await member.edit(deafen=deafen)
                did_edit = True
        if char_unmuted and did_edit:
            await self.notify_deafened(channel)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.deafen_for_char(before.channel)
        await self.deafen_for_char(after.channel)
        if await self.vc_is_just_char_and_lily(after.channel): self.enable_smh_mode()
        elif await self.vc_is_just_char_and_lily(before.channel): self.disable_smh_mode()
    @commands.command()
    async def charimg(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.MODERATOR): return
        self.no_images = not self.no_images
        await ctx.send(f'char can{"not" if no_images else ""} send images')
    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.app.bot.get_context(msg)
        # pleading face
        if "🥺" in msg.content and random.randint(1, 10) == 10:
            await ctx.send(file=discord.File('/home/matt/pastabot/wtf.png'))
        if str(msg.author.id) != self.CHAR: return
        # smh char talk to your girlfriend
        if await self.vc_is_just_char_and_lily(msg.channel):
            say_smh = enable_smh = False
            if not self.app.config.exists('smh'): say_smh = enable_smh = True
            elif self.app.config.get('smh')['enabled']: say_smh = True
            elif time.time() - self.app.config.get('smh')['time'] > 3600: say_smh = enable_smh = True
            if not self.app.config.exists('tts'): say_smh = enable_smh = False
            elif self.CHAR not in self.app.config.get('tts'): say_smh = enable_smh = False
            elif str(ctx.channel.id) not in self.app.config.get('tts')[self.CHAR]: say_smh = enable_smh = False
            if msg.content.lower().strip() == 'i hate lily' and say_smh:
                say_smh = enable_smh = False
                self.disable_smh_mode()
                await ctx.send('ok, overridden for one hour')
            if enable_smh: self.enable_smh_mode()
            if say_smh: 
                if self.app.config.exists('tts') and self.CHAR in self.app.config.get('tts'):
                    self.app.config.get('tts')[self.CHAR] = {}
                    self.app.config.save()
                await ctx.send('smh char talk to your girlfriend. can be overridden with "i hate lily"')
        else: self.disable_smh_mode()
        # none of that
        if self.no_images and msg.attachments:
            for attachment in msg.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    await msg.delete()
                    await msg.channel.send("none of that")
                    break
