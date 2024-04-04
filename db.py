import json

class database:
    def load(self):
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
            with open(config["storage"]) as storage:
                return json.loads(storage.read())
    def __init__(self):
        self.db = self.load()
    def save(self):
        if self.db == None:
            return
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
            with open(config["storage"], "w") as storage:
                storage.write(json.dumps(self.db))
    def get(self, player_id):
        if player_id in self.db:
            return self.db[player_id]
        return None
    def player_id(self, player):
        return player["ID"]
    def player_names(self, player):
        return player["NAME"]
    def player_discords(self, player):
        if "Discord_ID" not in player:
            return []
        if isinstance(player["Discord_ID"], str):
            return [player["Discord_ID"]]
        return player["Discord_ID"]
    def query_id(self, player_id):
        if player_id in self.db:
            return [self.db[player_id]]
        return []
    def query_name(self, name):
        name = name.lower()
        players = []
        for key in self.db:
            player = self.db[key]
            for player_name in player["NAME"]:
                if name in player_name.lower():
                    players.append(player)
                    break
        return players
    def player_string(self, player):
        pstr = "--------------------------------------\n"
        pstr += f'{player["NAME"][-1]}   [{player["ID"]}]\n'
        for i in range(len(player["NAME"])):
            pstr += player["NAME"][i]
            if i + 1 < len(player["NAME"]):
                pstr += ", "
        return pstr
    def player_list_to_string(self, player_list):
        if player_list == []:
            return "No data"
        pstr = ""
        for player in player_list:
            pstr += self.player_string(player) + "\n"
        return pstr



db = database()
