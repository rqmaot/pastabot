from discord.ext import commands

from app import Auth, command

class Counter(commands.Cog):
    def __init__(self, app):
        self.app = app
    async def get_count(self, init=0):
        async with self.app.config as config:
            return config.get_or('count', init)
    async def incr(self, delta=1, init=0):
        async with self.app.config as config:
            config['count'] = config.get_or('count', init) + delta
        return config['count']
    @command(help='Get the lily counter')
    async def lils(self, ctx):
        await ctx.send(await self.get_count())
    @command(help='Increment the lily counter', auth=Auth.TRUSTED)
    async def lilsplus(self, ctx):
        await ctx.send(str(await self.incr()))
    @command(help='Decrement the lily counter', auth=Auth.TRUSTED)
    async def lilsminus(self, ctx):
        await ctx.send(str(await self.incr(-1)))
