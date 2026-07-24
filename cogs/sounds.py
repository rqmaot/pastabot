from discord.ext import commands
import json
import os
from pathlib import Path

class Sounds(commands.Cog):
    def __init__(self, app):
        self.app = app
    @commands.command(help='Clear the sound queue')
    async def clear(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.NOAUTH): return
        self.app.musicq.clear()
        await ctx.send("cleared the queue")
    def get_sound(self, sound, root=None):
        sounds = self.app.config.get('sounds')
        if root is None: root = sounds['prefix']
        parts = sound.split('/')
        subdirs = []
        for f in sorted(os.listdir(root)):
            subpath = os.path.join(root, f)
            if Path(subpath).is_dir():
                if len(parts) > 1 and parts[0].lower() in f.lower():
                    sub = self.get_sound('/'.join(parts[1:]), subpath)
                    if sub is not None: return sub
                subdirs.append(subpath)
                continue
            if sound.lower() in f.lower(): return subpath
        for subdir in subdirs:
            sub = self.get_sound(sound, subdir)
            if sub is not None: return sub
        return None
    @commands.command(help='Play a sound by its name/path')
    async def sound(self, ctx, *sound):
        if await self.app.auth.verify(ctx, self.app.auth.NOAUTH): return
        sound = ' '.join(sound).strip()
        try: vc = await self.app.connect_to_vc(ctx)
        except:
            await ctx.send('could not connect to voice')
            return
        try:
            file = self.get_sound(sound)
            if file is None:
                await ctx.send('no such sound')
                return
            self.app.musicq.add(file, vc=vc)
        except Exception as e:
            await ctx.send(f'sounds.sound: {e}')
    @commands.command(help='Connect the bot to the VC you\'re in')
    async def join(self, ctx):
        try: await self.app.connect_to_vc(ctx)
        except: await ctx.send(f'sounds.join: {e}')
    @commands.command(help='Disconnect the bot from VC')
    async def leave(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.NOAUTH): return
        await ctx.voice_client.disconnect()
    @commands.command(help='Stop the currently playing sound')
    async def stop(self, ctx, track=None):
        if await self.app.auth.verify(ctx, self.app.auth.NOAUTH): return
        try: track = int(track)
        except: track = None
        try:
            vc = ctx.guild.voice_client
            self.app.musicq.stop(vc, track)
        except Exception as e:
            await ctx.send(f'sounds.stop: {e}')
    def get_list(self, query, path=None):
        root = self.app.config.get("sounds")["prefix"]
        if path is None: path = root
        parts = query.split('/')
        subdirs = []
        for f in sorted(os.listdir(path)):
            subpath = os.path.join(path, f)
            if not Path(subpath).is_dir(): continue
            subdirs.append(subpath)
            if parts[0].lower() not in f.lower(): continue
            if len(parts) > 1:
                sub = self.get_list("/".join(parts[1:]), subpath)
                if sub is not None: return sub
                continue
            files = []
            dirs = []
            for f1 in sorted(os.listdir(subpath)):
                subsubpath = os.path.join(subpath, f1)
                name = subsubpath[(len(root) + 1):]
                if Path(subsubpath).is_dir(): dirs.append(name + "/")
                else: files.append(name)
            return "\n".join(files + dirs)
        for subdir in subdirs:
            sub = self.get_list(query, subdir)
            if sub is not None: return sub
        return None
    @commands.command(help='Get a list of sounds, optionally under a particular directory')
    async def sounds(self, ctx, query=None):
        if query is None:
            await ctx.send('sounds:')
            files = []
            dirs = []
            root = self.app.config.get('sounds')['prefix']
            for path in sorted(os.listdir(root)):
                if Path(os.path.join(root, path)).is_dir(): dirs.append(path + '/')
                else: files.append(path)
            await ctx.send('\n'.join(files + dirs))
            return
        res = self.get_list(query)
        if res is None:
            await ctx.send('No sounds found. Try with no arguments for root list')
        else:
            await ctx.send(f'{query} sounds:\n{res}')
