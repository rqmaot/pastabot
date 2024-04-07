import json

class database:
    horizontal_line = "--------------------------------------\n"
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
    def put(self, player_id, name, discord_id):
        if player_id in self.db:
            if name in self.db[player_id]["NAME"]:
                i = self.db[player_id]["NAME"].index(name)
                del self.db[player_id]["NAME"][i]
            self.db[player_id]["NAME"].append(name)
            if isinstance(self.db[player_id]["Discord_ID"], str):
                self.db[player_id]["Discord_ID"] = [self.db[player_id]["Discord_ID"]]
            if discord_id not in self.db[player_id]["Discord_ID"]:
                self.db[player_id]["Discord_ID"].append(discord_id)
        else:
            self.db[player_id] = {
                "ID": player_id,
                "NAME": [name],
                "Discord_ID": [discord_id]
            }
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
        pstr = self.horizontal_line
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
    def _parse_list_line(self, line):
        i = line.find('"')
        line = line[i + 1:]
        i = line.find('"')
        name = line[0:i]
        line = line[i+1:]
        i = line.find('[')
        line = line[i+1:]
        i = line.find(']')
        player_id = line[0:i]
        if player_id == "YOU":
            line = line[i+1:]
            i = line.find('[')
            line = line[i+1:]
            i = line.find(']')
            player_id = line[0:i]
        line = line[i+1:]
        i = line.find('[')
        line = line[i+1:]
        i = line.find(']')
        discord_id = line[0:i]
        return (name, player_id, discord_id)
    def parse_list(self, liststr):
        lines = liststr.split('\n')
        res = []
        for line in lines:
            name, player_id, discord_id = self._parse_list_line(line)
            self.put(player_id, name, discord_id)
            query = self.query_id(player_id)
            res.append((name, player_id, discord_id, query))
        self.save()
        return res
    def list_messages(self, list_response):
        messages = []
        cur = ""
        for (name, player_id, discord, query) in list_response:
            next_line = f"{self.horizontal_line}- {name} ({player_id})\n"
            if len(cur) + len(next_line) >= 1500:
                messages.append(cur)
                cur = ""
            cur += next_line
            player_names = "No data" if query == [] else self.player_string(query[0]).split('\n')[2]
            if len(cur) + len(player_names) >= 1500:
                messages.append(cur)
                cur = ""
            if len(player_names) >= 1500:
                individual_names = player_names.split(', ')
                for player_name in individual_names:
                    if len(cur) + 2 + player_name >= 1500:
                        messages.append(cur)
                        cur = ""
                    cur += player_name if cur == "" else f", {player_name}"
                if cur != "":
                    messages.append(cur)
                    cur = ""
            else:
                cur += player_names
            cur += "\n"
        if cur != "":
            messages.append(cur)
        return messages


db = database()
