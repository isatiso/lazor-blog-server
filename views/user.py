# coding:utf-8
"""Views' Module of User."""
from hashlib import md5
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED
from workers.task_database import TASKS as tasks


class User(BaseHandler):
    """Handler account stuff."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_json_arguments(name=ENFORCED, password=ENFORCED)

        user_info = tasks.query_user(username=args.name)

        if not user_info:
            user_info = tasks.query_user(email=args.name)

        if not user_info:
            return self.fail(3011)

        if user_info['pswd'] != md5(args.password.encode()).hexdigest():
            return self.fail(3001)

        if not user_info['active_status']:
            return self.fail(3002)

        user_params = dict(
            user_name=user_info['username'],
            email=user_info['email'],
            user_id=user_info['user_id'])

        self.set_current_user(user_info['user_id'])
        self.set_parameters(user_params)

        self.success(data=user_params)

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        args = self.parse_json_arguments(
            username=ENFORCED, email=ENFORCED, password=ENFORCED)

        if not self.pattern_match('email', args.email):
            return self.fail(3032)
        if not self.pattern_match('password', args.password):
            return self.fail(3031)

        exists_result = tasks.query_email_or_username_exists(
            username=args.username, email=args.email)
        if exists_result:
            return self.fail(3004)

        insert_result = tasks.insert_user(
            username=args.username,
            email=args.email,
            pswd=md5(args.password.encode()).hexdigest())

        insert_result = tasks.insert_category(
            category_name='默认分类',
            category_type=0,
            user_id=insert_result['data']['user_id'])

        self.success()

    def delete(self, *_args, **_kwargs):
        self.set_current_user('')
        self.set_parameters(dict())
        self.success()


class UserProfile(BaseHandler):
    """Handler account info stuff."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(name=ENFORCED)

        exists_result = tasks.query_username_exists(username=args.name)

        if exists_result:
            return self.fail(3004)

        tasks.update_user_name(user_id=_params.user_id, username=args.name)

        _params.add('user_name', args.name)
        self.set_parameters(_params[0])

        self.success()

class UserPassword(BaseHandler):
    """Handle password of account."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(old_pass=ENFORCED, new_pass=ENFORCED)

        user_info = tasks.query_user(user_id=_params.user_id)

        if not user_info:
            return self.fail(4004)

        old_md5 = md5(args.old_pass.encode()).hexdigest()
        new_md5 = md5(args.new_pass.encode()).hexdigest()

        if old_md5 != user_info['pswd']:
            print(old_md5, user_info['pswd'])
            return self.fail(3001)

        tasks.update_user_pass(user_id=_params.user_id, pswd=new_md5)

        self.success()

        # exists_result = tasks.query_username_exists(username=args.name)

        # if exists_result:
        #     return self.fail(3004)

USER_URLS = [
    (r'/user', User),
    (r'/user/profile', UserProfile),
    (r'/user/password', UserPassword)
]
