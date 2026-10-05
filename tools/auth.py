import json
from functools import cache

class Auth:
    BLACKLIST = 0
    NOAUTH = 1
    TRUSTED = 2
    MODERATOR = 4
    ADMIN = 8
    @cache
    @staticmethod
    def name_to_level(name=None):
        themap = {'blacklist': Auth.BLACKLIST,
                  'noauth': Auth.NOAUTH,
                  'trusted': Auth.TRUSTED,
                  'moderator': Auth.MODERATOR,
                  'admin': Auth.ADMIN}
        return themap if name is None else themap[name]
    @cache
    @staticmethod
    def level_to_name(level=None):
        themap = {Auth.BLACKLIST: 'blacklist',
                  Auth.NOAUTH: 'noauth',
                  Auth.TRUSTED: 'trusted',
                  Auth.MODERATOR: 'moderator',
                  Auth.ADMIN: 'admin'}
        return themap if level is None else themap[level]
    def __init__(self, config):
        self.config = config
    def check(self, discord_id):
        # verify that config contains auth info
        if 'auth' not in self.config:
            print('no auth in config')
            return self.NOAUTH
        # check all the permissions
        for name in Auth.name_to_level():
            if name not in self.config['auth']: continue
            if str(discord_id) in self.config['auth'][name]:
                return Auth.name_to_level(name)
        return self.NOAUTH
    async def verify(self, ctx, min_auth):
        if min_auth not in Auth.level_to_name():
            min_auth = Auth.NOAUTH
        if self.check(ctx.author.id) < min_auth:
            await ctx.send("you are not authorized to use this command")
            return True
        return False
    def get_auth_string(self, user_id):
        return Auth.level_to_name(self.check(user_id))
    async def update_auth(self, ctx, tgt_id, tgt_name, auth_name):
        user_auth = self.check(int(ctx.author.id))
        tgt_auth = self.check(int(tgt_id))
        if auth_name not in Auth.name_to_level():
            await ctx.send(f'Unknown auth level "{auth_name}". Possible levels: {', '.join(Auth.name_to_level())}')
            return
        level = Auth.name_to_level(auth_name)
        if user_auth <= tgt_auth:
            await ctx.send('You can only modify auth for those with less auth than you')
            return
        if user_auth <= level:
            await ctx.send('You can only set someone\'s auth up to the level below you')
            return
        if tgt_auth == level:
            await ctx.send(f'{tgt_name} already has auth level {auth_name}')
            return
        async with self.config as config:
            orig_auth = Auth.level_to_name(tgt_auth)
            if str(tgt_id) in config.get_or('auth', {}).get_or(orig_auth, {}):
                del config['auth'][orig_auth][str(tgt_id)]
            if orig_auth == 'noauth': del config['auth']['noauth']
            if auth_name != 'noauth':
                config['auth'].get_or(auth_name, {})[str(tgt_id)] = tgt_name
        await ctx.send('updated auth')
