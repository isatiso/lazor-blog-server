# coding:utf-8
"""Views' Module of Article."""
import re
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from config import CFG as config
from workers.task_database import TASKS as tasks


class Article(BaseHandler):
    """Handler article stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(3)
        if not _params:
            return

        

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(3)
        if not _params:
            return

        args = self.parse_json_arguments(
            title=ENFORCED,
            content=ENFORCED,
            category_id=OPTIONAL)

        insert_result = tasks.insert_article(
            user_id=_params.user_id,
            title=args.title,
            content=args.content,
            category_id=args.get('category_id', 'default'))

        self.success()

ARTICLE_URLS = [
    (r'/article', Article),
]
