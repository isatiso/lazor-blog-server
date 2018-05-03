# coding:utf-8
"""Arguments class, a wrapper of dict."""


class Arguments(dict):
    """Class to manage arguments of a requests."""

    def __init__(self, params):
        if isinstance(params, dict):
            super().__init__(params)
        elif not params:
            super().__init__(dict())
        else:
            raise TypeError(
                f"Arguments data should be a 'dict' not {type(params)}.")

    def __getattr__(self, name):
        attr = self.get(name)
        if isinstance(attr, dict):
            attr = self.__class__(attr)
        return attr

    def __setattr__(self, name, value):
        raise PermissionError('Can not set attribute to <class Arguments>.')

    def insert(self, key, value):
        """Add a variable to args."""
        if key in self:
            raise PermissionError(f'Key {key} is already exists.')
        else:
            self[key] = value
