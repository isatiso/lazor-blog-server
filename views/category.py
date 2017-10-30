# coding:utf-8
"""Views' Module of Article."""
import re
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from config import CFG as config
from workers.task_database import TASKS as tasks


class Category(BaseHandler):
    """Handler category stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        query_result = tasks.query_category_by_user_id(
            user_id=_params.user_id)

        self.success(data=query_result)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(
            category_id=ENFORCED,
            category_name=ENFORCED)

        update_result = tasks.update_category_name(
            category_id=args.category_id,
            category_name=args.category_name)

        print(update_result)
        
        self.success()

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(
            category_name=ENFORCED)

        insert_result = tasks.insert_category(
            category_name=args.category_name,
            category_type=1,
            user_id=_params.user_id)

        self.success()

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_form_arguments(
            category_id=ENFORCED)

        delete_result = tasks.delete_category(
            category_id=args.category_id)

        _update_result = tasks.update_article_category_by_user_id(
            user_id=_params.user_id, category_id=args.category_id)

        self.success(data=delete_result)


CATEGORY_URLS = [
    (r'/category', Category),
]
