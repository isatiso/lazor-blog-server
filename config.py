# coding:utf-8
"""Config Module."""

import yaml
from tornado.options import define, options

define('port', default=0)
define('env', default='test')

options.parse_command_line()
_ENV = options.env


class Config:
    """Config class to provide configuration."""

    def __init__(self, params):
        if isinstance(params, dict):
            self.config = params
        else:
            raise TypeError("Config can only initial with <class 'dict'>")

    def __getattr__(self, name):
        attr = self.config.get(name)
        if isinstance(attr, dict):
            if _ENV in attr.keys():
                return attr[_ENV]
            else:
                return Config(attr)
        else:
            return attr

    def __getitem__(self, key):
        if key in self.config:
            return self.config[key]
        else:
            KeyError(f"Unrecognized option {key}")

    def traverse(self, pre=''):
        """Traverse a Config instance."""
        all_config = dict()
        for key in self.config:
            if isinstance(self.config[key], dict):
                if _ENV in self.config[key].keys():
                    all_config[pre + key] = self.config[key][_ENV]
                else:
                    all_config.update(
                        self.__getattr__(key).traverse(pre + key + '.'))
            else:
                all_config[pre + key] = self.config[key]

        return all_config

    def fillup1(self):
        """Useless method to fill a class."""
        pass


CFG = None
try:
    with open('config.yaml', 'r') as config:
        CFG = Config(yaml.load(config))
except FileNotFoundError:
    CFG = Config({})
