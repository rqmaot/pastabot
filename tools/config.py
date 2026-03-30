import json

class Config:
    def __init__(self, path):
        self.path = path
        with open(path, 'r') as f:
            self.json = json.loads(f.read())
    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.json, f, indent=2)
    def get(self, key):
        if isinstance(key, list):
            obj = self.json
            for k in key:
                obj = obj[k]
            return obj
        return self.json[key]
    def set(self, key, val):
        if isinstance(key, list):
            obj = self.json
            for k in key[:-1]: obj = obj[k]
            obj[key[-1]] = val
            return
        self.json[key] = val
    def add(self, key, val):
        try:
            self.json[key]
            return False
        except:
            self.json[key] = val
            return True
    def exists(self, key):
        try:
            self.json[key]
            return True
        except: return False



