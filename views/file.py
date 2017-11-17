# coding:utf-8
"""Views' Module of Article."""
import re
import os
from uuid import uuid1 as uuid
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from utils.utils import generate_id
from config import CFG as config
from workers.task_database import TASKS as tasks


class File(BaseHandler):
    """Handler file stuff."""

    # @asynchronous
    # @coroutine
    # def get(self, *_args, **_kwargs):
    #     args = self.parse_form_arguments(article_id=ENFORCED)

    #     query_result = tasks.query_article(article_id=args.article_id)

    #     self.success(data=query_result)

    # @asynchronous
    # @coroutine
    # def post(self, *_args, **_kwargs):
    #     _params = self.check_auth(2)
    #     if not _params:
    #         return

    #     args = self.parse_json_arguments(
    #         article_id=ENFORCED,
    #         title=OPTIONAL,
    #         content=OPTIONAL,
    #         category_id=OPTIONAL)

    #     check_list = ('title', 'content', 'category_id')
    #     update_dict = dict(
    #         (arg, args.get(arg)) for arg in args.arguments if arg in check_list)

    #     update_result = tasks.update_article(
    #         article_id=args.article_id, **update_dict)

    #     self.success(data=update_result)

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        file_meta = self.request.files

        filename, ext = os.path.splitext(file_meta['file'][0]['filename'])
        file_id = str(uuid())
        with open('../static/image/' + file_id + ext, 'wb') as f:
            f.write(file_meta['file'][0]['body'])

        self.success(data=dict(
            file_id=file_id,
            file_path='/image/' + file_id + ext,
            file_name=filename+ext
        ))



FILE_URLS = [
    (r'/file', File),
]
