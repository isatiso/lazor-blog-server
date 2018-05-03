# coding:utf-8
"""Views' Module of Article."""

from uuid import uuid1 as uuid
import time
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL


class AccessLog(BaseHandler):
    """Handler image stuff."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        pass


class Credit(BaseHandler):
    """Handle credit stuff."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        # _params = yield self.check_auth()
        _params = self.get_parameters()
        if _params:
            self.session.update(
                {
                    'ip': self.request.remote_ip
                }, {
                    '$set': {
                        'user_id': _params.user_id,
                        'user_name': _params.user_name
                    }
                },
                upsert=True)

        args = self.parse_json_arguments('credit', 'page', description=None)

        description = args.description or dict()

        mixin = self.get_secure_cookie('koo').decode()

        session = self.session.find_one({'ip': self.request.remote_ip})

        if not session:
            self.fail(4003)

        current_mixin = session.get('mixin')

        if current_mixin != mixin:
            self.fail(4003)

        b = self.get_cookie('koo').split('|')[-1]
        current_credit = md5(b.encode()).hexdigest()

        if current_credit != args.credit:
            self.fail(4003)

        description.update(
            dict(
                ip=self.request.remote_ip,
                page=args.page,
                time=int(time.time()),
                user_id=session.get('user_id', 'anonymous'),
                user_name=session.get('user_name', ''),
                session_id=session.get('session_id', '')))

        self.access_log.insert(description)

        if str(time.time())[-1] == '4':
            base = str(time.time()).encode()
            credit = md5(base).hexdigest()

            self.session.update({
                'ip': self.request.remote_ip
            }, {'$set': {
                'mixin': credit
            }})

            self.set_secure_cookie(
                'koo', credit.encode(), domain=self.request.host)

        self.success()


class Favicon(BaseHandler):
    """Handle icon."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        base = str(time.time()).encode()
        credit = md5(base).hexdigest()

        self.session.update(
            {
                'ip': self.request.remote_ip
            }, {'$set': {
                'mixin': credit,
                'session_id': uuid().hex
            }},
            upsert=True)

        self.set_secure_cookie(
            'koo', credit.encode(), domain=self.request.host)
        self.redirect('https://lazor.cn/assets/js/loading.js')
        # res = yield self.fetch('https://lazor.cn/assets/js/loading.js')
        # self.finish(res.res_body)

