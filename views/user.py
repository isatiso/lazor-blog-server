# coding:utf-8
"""Views' Module of User."""
import re
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from config import CFG as config
from workers.task_database import TASKS as tasks


class User(BaseHandler):
    """Handler account stuff."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_json_arguments(
            username=OPTIONAL,
            email=OPTIONAL,
            password=ENFORCED)

        if args.username:
            if not self.pattern_match('password', args.password):
                return self.fail(3031)
            user_info = tasks.query_user(username=args.username)
        elif args.email:
            if not self.pattern_match('email', args.email):
                return self.fail(3032)
            user_info = tasks.query_user(email=args.email)
        else:
            return self.fail(3016)

        if not user_info:
            return self.fail(3011)

        if user_info['pswd'] != md5(args.password.encode()).hexdigest():
            return self.fail(3001)

        self.set_current_user(user_info['user_id'])
        self.set_parameters(dict(
            username=user_info['username'],
            email=user_info['email'],
            user_id=user_info['user_id']))

        self.success()

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        args = self.parse_json_arguments(
            username=ENFORCED,
            email=ENFORCED,
            password=ENFORCED)

        if not self.pattern_match('email', args.email):
            return self.fail(3032)
        if not self.pattern_match('password', args.password):
            return self.fail(3031)

        exists_result = tasks.query_email_or_username_exists(
            username=args.username,
            email=args.email)
        if exists_result:
            return self.fail(3004)

        insert_result = tasks.insert_user(
            username=args.username,
            email=args.email,
            pswd=md5(args.password.encode()).hexdigest())

        self.success()


USER_URLS = [
    (r'/user', User),
]
