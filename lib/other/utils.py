# coding:utf-8
"""Module of some useful tools."""

import random
import re
import time
from hashlib import md5


def create_random_code():
    """Create a random code with time and md5."""
    return md5(str(time.time()).encode()).hexdigest()


def generate_id(namespace='0000'):
    """Create an ID."""
    timep = hex(int(time.time() * 1000))[2:]
    rands = f'{random.randint(0, 65536):04x}'
    return f'{namespace}-{timep[4:8]}-{timep[:4]}-{rands}-{timep[8:]}'


class Tasks:
    """Manager Class of Tasks."""

    def __init__(self, params):
        if isinstance(params, dict):
            self.tasks = params
        else:
            raise TypeError(
                f'Arguments data should be a "dict" not {type(params)}.')

    def __getattr__(self, task_name):
        return self._get_task(task_name)

    def __iter__(self):
        for i in self.tasks:
            yield i

    def __getitem__(self, task_name):
        return self._get_task(task_name)

    def to_dict(self):
        """Return the task dictionary."""
        return self.tasks

    def keys(self):
        """Return the keys of the task dictionary."""
        return self.tasks.keys

    def _get_task(self, name):
        task = self.tasks.get(name)
        if task is None:
            raise KeyError(name)
        else:
            return task
