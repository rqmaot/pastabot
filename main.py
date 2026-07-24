import asyncio
import discord
from discord.ext import commands
import importlib.util
import inspect
import os
from pathlib import Path
import subprocess

from cogs import basics
from cogs import cipher
from cogs import counter
from cogs import ftp
from cogs import rng
from cogs import moderation

from tools.auth import Auth
from tools.config import Config
from tools import musicq

class App:
    def __init__(self):
        self.config = Config('config.json')
        self.auth = Auth(self.config)
        self.musicq = musicq.Queue()
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents)
    def run(self):
        TOKEN = self.config.get('token')
        self.bot.run(TOKEN)
    async def add_cogs(self, cog_dir):
        end = 0
        for file in Path(cog_dir).glob('*.py'):
            if file.name.startswith('_'): continue
            try:
                name = file.name.replace(' ', '_') + f'_{end}'
                path = os.path.join(cog_dir, file.name)
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                for _, mod_class in inspect.getmembers(mod, inspect.isclass):
                    if not issubclass(mod_class, commands.Cog): continue
                    await self.bot.add_cog(mod_class(self))
                end += 1
            except Exception as e:
                print(f'Failed to load {path}: {e}')
    async def connect_to_vc(self, ctx):
        vc = ctx.voice_client
        if vc is None:
            async with self.musicq.lock: 
                vc = await ctx.author.voice.channel.connect()
        return vc
    def get_ip(self):
        return str(subprocess.check_output(['curl', 'ipinfo.io/ip']))[2:-1]

app = App()
asyncio.run(app.add_cogs('cogs'))

if __name__ == '__main__':
    subprocess.run(['rm', '-rf', 'tts'], capture_output=True)
    app.run()
