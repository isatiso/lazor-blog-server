# coding:utf-8
"""Views' Module of Guard Interface."""
import re
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler
from config import CFG as config


class AddressGuard(BaseHandler):
    """Handler account stuff."""

    if config.access_mode == 'reg':
        address_pattern = re.compile(config.access_regex)
    else:
        address_pattern = re.compile(r'')

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        if config.access_mode == 'reg':
            if not re.match(self.address_pattern, self.request.remote_ip):
                return self.dump_fail_data(3012)
        else:
            if self.request.remote_ip not in config.access_list:
                return self.dump_fail_data(3012)

        user_info = self.wcd_user.find_one({'user_ip': self.request.remote_ip})
        if user_info:
            user_info = dict(
                user_ip=user_info['user_ip'], nickname=user_info['nickname'])

        res = dict(result=1, status=0, msg='Successfully.', data=user_info)
        self.finish_with_json(res)
