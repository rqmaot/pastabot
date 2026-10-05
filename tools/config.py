import asyncio
import json as mod_json
import threading

class Config:
    def __init__(self, path=None, parent=None, json=None, is_async=False):
        self.path = path
        self.parent = parent
        self.json = json
        self.is_async = is_async if parent is None else parent.is_async
        self.mutex = asyncio.Lock() if self.is_async else threading.Lock()
        if path is not None:
            try:
                with open(path, 'r') as f:
                    self.json = mod_json.loads(f.read())
            except FileNotFoundError:
                self.json = {}
    @staticmethod
    def is_json(val):
        if True in map(lambda t: isinstance(val, t),
                       [int, float, str, bool, type(None)]):
            return True
        if isinstance(val, dict):
            for key in val:
                if not isinstance(key, str): return False
                if not Config.is_json(val[key]): return False
            return True
        if isinstance(val, list):
            return False not in map(Config.is_json, val)
        return False
    def root(self):
        config = self
        while config.parent is not None: config = config.parent
        return config
    def save(self):
        config = self.root()
        with open(config.path, 'w') as f:
                mod_json.dump(config.json, f, indent=2)
    def __getitem__(self, key):
        if isinstance(self.json[key], list) or isinstance(self.json[key], dict):
            return Config(parent=self, json=self.json[key])
        return self.json[key]
    def __contains__(self, key): return key in self.json
    def __len__(self): return len(self.json)
    def __iter__(self):
        if isinstance(self.json, dict): return iter(self.json)
        if isinstance(self.json, list):
            class ConfigListIterator:
                def __init__(self, config):
                    self.config = config
                    self.i = 0
                def __next__(self):
                    if self.i < len(self.config):
                        self.i += 1
                        return self.config[self.i - 1]
                    raise StopIteration
            return ConfigListIterator(self)
        raise ValueError(f'cannot iterate over this: {self.json}')
    class WritableConfig:
        def __init__(self, config):
            self.config = config
        def __getitem__(self, key): 
            res = self.config[key]
            if isinstance(res, Config): return Config.WritableConfig(res)
            return res
        def __contains__(self, key): return key in self.config
        def __len__(self): return len(self.config)
        def __iter__(self): 
            writable = lambda x: Config.WritableConfig(x) if isinstance(x, Config) else x
            return map(writable, iter(self.config))
        def __setitem__(self, key, val):
            assert Config.is_json(val), f'invalid JSON: {val}'
            self.config.json[key] = val
        def __delitem__(self, key):
            del self.config.json[key]
        def append(self, val):
            assert isinstance(self.config.json, list), 'Config.append: can only append to lists'
            assert Config.is_json(val), f'invalid JSON: {val}'
            self.config.json.append(val)
        def remove(self, val):
            if isinstance(self.config.json, list):
                removed = False
                i = 0
                while i < len(self.config.json):
                    if self.config.json[i] == val: 
                        del self.config.json[i]
                        removed = True
                    else: i += 1
                return removed
            else: raise ValueError('Config.remove: called on non-list')
        def get_or(self, key, default):
            assert Config.is_json(default), f'invalid JSON: {default}'
            if key not in self: self[key] = default
            return self[key]
    def __enter__(self):
        assert not self.is_async, 'this is an async config. use `async with` instead'
        self.mutex.acquire()
        return Config.WritableConfig(self) 
    def __exit__(self, exc_type, exc_value, traceback):
        self.save()
        self.mutex.release()
        return False
    async def __aenter__(self):
        assert self.is_async, 'this is not an async config. use normal `with` instead'
        await self.mutex.acquire()
        return Config.WritableConfig(self)
    async def __aexit__(self, exc_type, exc_value, traceback):
        self.save()
        self.mutex.release()
        return False

