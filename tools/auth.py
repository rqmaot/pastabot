import json

CONFIG = None

class Auth:
    def __init__(self):
        self.BLACKLIST = 0
        self.NOAUTH = 1
        self.TRUSTED = 2
        self.MODERATOR = 4
        self.ADMIN = 8
    def check(self, discord_id):
        # verify that config contains auth info
        try: _ = CONFIG.get(["auth"])
        except: 
            print("no auth")
            return self.BLACKLIST
        # function to check if they have a permission type
        def auth_check(auth_type):
            for entry in CONFIG.get(["auth", auth_type]):
                if int(entry["id"]) == int(discord_id):
                    return True
            return False
        # check all the permissions
        if auth_check("blacklist"):
            return self.BLACKLIST
        if auth_check("admin"):
            return self.ADMIN
        if auth_check("moderator"):
            return self.MODERATOR
        if auth_check("trusted"):
            return self.TRUSTED
        return self.NOAUTH
    async def verify(self, ctx, min_auth):
        if self.check(ctx.author.id) < min_auth:
            await ctx.send("you are not authorized to use this command")
            return True
        return False

auth = Auth()
