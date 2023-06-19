import _thread
try:
    import ujson as json
except:
    import json


class JsonConfigureHandler(object):
    GET = 0x01
    SET = 0x02
    DEL = 0x03

    def __init__(self, path, encoding='utf8'):
        self.path = path
        self.encoding = encoding
        self.lock = _thread.allocate_lock()
        self.settings = None
        self.load()  # first load setting from json file.

    def load(self, reload=False):
        if (self.settings is None) or reload:
            with self.lock:
                with open(self.path, 'r', encoding=self.encoding) as f:
                    self.settings = json.load(f)

    def reload(self):
        self.load(reload=True)

    def save(self):
        with self.lock:
            with open(self.path, 'w+', encoding=self.encoding) as f:
                json.dump(self.settings, f)

    def get(self, key):
        with self.lock:
            return self.execute(self.settings, key.split('.'), operate=self.GET)

    def __getitem__(self, item):
        return self.get(item)

    def set(self, key, value):
        with self.lock:
            return self.execute(self.settings, key.split('.'), value=value, operate=self.SET)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def delete(self, key):
        with self.lock:
            return self.execute(self.settings, key.split('.'), operate=self.DEL)

    def __delitem__(self, key):
        return self.delete(key)

    def execute(self, dict_, keys, value=None, operate=None):

        key = keys.pop(0)

        if len(keys) == 0:
            if operate == self.GET:
                return dict_[key]
            elif operate == self.SET:
                dict_[key] = value
            elif operate == self.DEL:
                del dict_[key]
            return

        if key not in dict_:
            if operate == self.SET:
                dict_[key] = {}  # auto create sub items recursively.
            else:
                return

        return self.execute(dict_[key], keys, value=value, operate=operate)


class ConfigureRegisterTable(object):

    register_table = {}

    @classmethod
    def get(cls, path):
        return cls.register_table.get(path)

    @classmethod
    def set(cls, path, config):
        cls.register_table[path] = config


def ConfigureHandler(path):
    registered_config = ConfigureRegisterTable.get(path)
    if registered_config is not None:
        return registered_config

    if path.endswith('.json'):
        config = JsonConfigureHandler(path)
        ConfigureRegisterTable.set(path, config)
        return config
    else:
        raise TypeError('file format not supported!')
