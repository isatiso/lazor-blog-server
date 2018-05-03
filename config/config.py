# coding:utf-8
"""Convert YAML to Python Data."""
import sys
import os
import json

import yaml
from tornado.options import define, options

from lib.arguments import Arguments

define('port', default=0)

options.parse_command_line()
_ENV = os.getenv('lazor_env', 'mypc')


class Config(Arguments):
    def __init__(self, params):
        super().__init__(self.convert(params))

    def traverse(self, pre=''):
        new_dict = dict()
        for key in self:
            if isinstance(self[key], dict):
                new_dict.update(
                    self.__getattr__(key).traverse(pre + key + '.'))
            else:
                new_dict[pre + key] = self[key]
        return new_dict

    def convert(self, params):
        new_dict = dict()
        for key in params:
            if isinstance(params[key], dict):
                if _ENV in params[key]:
                    new_dict[key] = params[key][_ENV]
                else:
                    new_dict[key] = self.convert(params[key])
            else:
                new_dict[key] = params[key]
        return new_dict

    def show(self):
        sys.stdout.write('\nconfig:\n')
        json.dump(self.traverse(), sys.stdout, indent=4, sort_keys=True)
        sys.stdout.write('\n\n\n')
        sys.stdout.flush()


CFG = None
try:
    with open('config/config.yaml', 'r', encoding='utf-8') as config:
        CFG = Config(yaml.load(config))
except FileNotFoundError:
    CFG = Config(dict(error='Config File Not Found.'))
