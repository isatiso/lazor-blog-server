# coding:utf-8
"""Views' Module of Guard Interface."""
import re
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from workers.task_database import TASKS as tasks
from config import CFG as config


class AuthGuard(BaseHandler):
    """Handler account stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            self.session.update({
                'ip': self.request.remote_ip
            }, {
                '$set': {
                    'user_id': ''
                }
            })
            return

        self.success(data=_params[0])


class ArticleOwnerGuard(BaseHandler):
    """Handler if user own the article."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_form_arguments(article_id=ENFORCED)

        query_result = tasks.query_article(article_id=args.article_id)

        if not query_result:
            return self.fail(4004)
        if _params.user_id != query_result['user_id']:
            return self.fail(4005)

        self.success()


GUARD_URLS = [
    (r'/guard/auth', AuthGuard),
    (r'/guard/owner', ArticleOwnerGuard),
]
