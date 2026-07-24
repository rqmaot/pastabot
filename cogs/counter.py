from discord.ext import commands

class Counter(commands.Cog):
    def __init__(self, app):
        self.app = app
    def get_count(self):
        if self.app.config.exists('count'):
            return self.app.config.get('count')
        return 0
    def incr(self, delta=1, init=1):
        if self.app.config.exists('count'):
            self.app.config.set('count', self.app.config.get('count') + delta)
            self.app.config.save()
            return self.app.config.get('count')
        self.app.config.add('count', init)
        self.app.config.save()
        return init
    @commands.command(help='Get the lily counter')
    async def lils(self, ctx):
        await ctx.send(self.get_count())
    @commands.command(help='Increment the lily counter')
    async def lilsplus(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        await ctx.send(str(self.incr()))
    @commands.command(help='Decrement the lily counter')
    async def lilsminus(self, ctx):
        if await self.app.auth.verify(ctx, self.app.auth.MODERATOR): return
        await ctx.send(str(self.incr(-1)))
