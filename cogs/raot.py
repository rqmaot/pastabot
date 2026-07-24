import discord
from discord.ext import commands
import json

class RAOT(commands.Cog):
    def __init__(self, app):
        self.app = app
        try:
            self.path = self.app.config.get('raot')
            with open(self.path) as f:
                self.json = json.loads(f.read())
        except Exception as e:
            print(f'raot.init: {e}')
            self.path = None
            self.json = None
    def save(self):
        if self.path is None or self.json is None: return
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.json, indent=2))
    def search_id(self, raot_id):
        if self.json is None: return []
        if raot_id in self.json: return [self.json[raot_id]]
        return []
    def search_name(self, name):
        if self.json is None: return []
        results = []
        for raot_id in self.json:
            if name.lower() in map(lambda n: n.lower(), self.json[raot_id]['NAME']):
                results.append(self.json[raot_id])
        return results
    def add_one(self, raot_id, name, discord_id):
        if self.json is None: 
            self.json = {raot_id: {'ID': raot_id, 'NAME': [name], 'Discord_ID': discord_id}}
            return self.json[raot_id]
        if raot_id not in self.json:
            self.json[raot_id] = {'ID': raot_id, 'NAME': [name], 'Discord_ID': discord_id}
            return self.json[raot_id]
        if name in self.json[raot_id]['NAME']: 
            del self.json[raot_id]['NAME'][self.json[raot_id]['NAME'].index(name)]
        self.json[raot_id]['NAME'].append(name)
        if discord_id != '0': self.json[raot_id]['Discord_ID'] = discord_id
        return self.json[raot_id]
    def add_list(self, list_dump):
        players = []
        for line in list_dump:
            try:
                name = line.split('"')[1]
                raot_id = str(int(line.split('[')[1].split(']')[0]))
                discord_id = str(int(line.split('[')[2].split(']')[0]))
                player = self.add_one(raot_id, name, discord_id)
                players.append(player)
            except: pass
        return players
    async def send_results(self, ctx, results):
        if len(results) == 0:
            await ctx.send('No results')
            return
        sep = '\n============================================================\n'
        msg = sep.join(map(lambda player:
            f'- {player["NAME"][-1]} ({player["ID"]})\n{", ".join(player["NAME"][::-1])}',
            results))
        curr = ''
        for line in msg.split('\n'):
            if len(curr) + len(line) > 1500:
                await ctx.send(curr)
                curr = line
            else: curr += '\n' + line
        if curr.strip() != '': await ctx.send(curr)
    @commands.command(help='Search a RAOT player by their ID')
    async def id(self, ctx, raot_id):
        try: await self.send_results(ctx, self.search_id(raot_id))
        except Exception as e: await ctx.send(f'raot.id: {e}')
    @commands.command(help='Search a RAOT player by their name')
    async def name(self, ctx, name):
        try: await self.send_results(ctx, self.search_name(name))
        except Exception as e: await ctx.send(f'raot.name: {e}')
    @commands.command(help='Check the DB for matches in an entire lobby from RAOT\'s list command')
    async def list(self, ctx, raot_list):
        try:
            results = self.add_list(raot_list)
            self.save()
            await self.send_results(ctx, results)
        except Exception as e: await ctx.send(f'raot.list: {e}')
    @commands.command(help='Get the raw JSON data for the RAOT database')
    async def dump(self, ctx):
        try: await ctx.send(file=discord.File(self.path))
        except Exception as e: await ctx.send(f'raot.dump: {e}')
