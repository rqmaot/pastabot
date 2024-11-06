import json

class Auth:
    def __init__(self):
        self.BLACKLIST = 0
        self.NOAUTH = 1
        self.TRUSTED = 2
        self.MODERATOR = 4
        self.ADMIN = 8
        self.regenerate()
    def regenerate(self):
        try:
            with open("config.json") as config_file:
                config = json.loads(config_file.read())
                self.auth = config["auth"]
        except Exception as e:
            print(f"Failed to generate auths: {e}")
            self.auth = None
    def check(self, discord_id):
        # if there's no auth file, no on has permissions
        if self.auth == None:
            return self.BLACKLIST
        # function to check if they have a permission type
        def auth_check(auth_type):
            for entry in self.auth[auth_type]:
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
