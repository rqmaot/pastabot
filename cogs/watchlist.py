from discord.ext import commands

class Watchlist(commands.Cog):
    def __init__(self, app):
        self.app = app
    def add(self, item):
        if not self.app.config.exists('watchlist'): self.app.config.add('watchlist', [])
        self.app.config.get('watchlist').append(item)
        self.app.config.save()
    def remove_item(self, item):
        lines = self.app.config.get('watchlist')
        try:
            i = lines.index(item)
            res = lines[i]
            del lines[i]
            self.app.config.save()
            return res
        except: return False
    def remove_index(self, i):
        try:
            res = self.app.config.get('watchlist')[i - 1]
            del self.app.config.get('watchlist')[i - 1]
            self.app.config.save()
            return res
        except Exception as e: 
            # print(f'watchlist.remove_index: {e}')
            return False
    async def ls(self, ctx):
        try: lines = self.app.config.get('watchlist')
        except: lines = None
        if lines is None or len(lines) == 0:
            await ctx.send('The watchlist is empty')
            return
        i = 1
        buf = ''
        for item in lines:
            new_buf = buf + f'\n{i}. {item}' if i > 1 else f'{i}. {item}'
            if len(new_buf) > 2000:
                await ctx.send(buf)
                buf = f'{i}. {item}'
            else: buf = new_buf
            i += 1
        await ctx.send(buf)
    @commands.command(help='Show watch list, or provide an item to add')
    async def watch(self, ctx, *item):
        item = ' '.join(item).strip()
        if item == '': return await self.ls(ctx)
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        self.add(item)
        await ctx.send(f'Added {item} to watchlist')
    @commands.command(help='Remove an item from the watch list by its name or index')
    async def watched(self, ctx, *item):
        if await self.app.auth.verify(ctx, self.app.auth.TRUSTED): return
        item = ' '.join(item).strip()
        by_item = self.remove_item(item)
        if by_item:
            await ctx.send(f'Removed {by_item} from watchlist')
            return
        try:
            by_index = self.remove_index(int(item))
            if by_index:
                await ctx.send(f'Removed {by_index} from watchlist')
                return
        except: pass
        await ctx.send(f'Could not find {item} on watchlist. Try !watch to see the list')
