import json

class Auth:
    def __init__(self):
        self.NOAUTH = 0
        self.TRUSTED = 1
        self.MODERATOR = 2
        self.ADMIN = 4
        try: 
            with open("config.json") as config_file:
                config = json.loads(config_file.read())
                with open(config["auth"]) as authfile:
                    self.auth = json.loads(authfile.read())
        except:
            self.auth = None
    def check(self, discord_id):
        # if there's no auth file, no on has permissions
        if self.auth == None:
            return self.NOAUTH
        # function to check if they have a permission type
        def auth_check(auth_type):
            for entry in self.auth[auth_type]:
                if int(entry["id"]) == int(discord_id):
                    return True
            return False
        # check all the permissions
        if auth_check("admin"):
            return self.ADMIN
        if auth_check("moderator"):
            return self.MODERATOR
        if auth_check("trusted"):
            return self.TRUSTED
        return self.NOAUTH

auth = Auth()
