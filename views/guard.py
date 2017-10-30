# coding:utf-8
"""Views' Module of Guard Interface."""
import re
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler
from config import CFG as config


class AuthGuard(BaseHandler):
    """Handler account stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        res = dict(result=1, status=0, msg='Successfully.', data=_params[0])
        self.finish_with_json(res)


GUARD_URLS = [
    (r'/guard/auth', AuthGuard),
]
