# coding:utf-8
"""Views' Module of Article."""
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from utils.utils import generate_id
from workers.task_database import TASKS as tasks


class Article(BaseHandler):
    """Handler article stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments(article_id=ENFORCED)

        query_result = tasks.query_article(article_id=args.article_id)
        if not query_result:
            self.fail(4004)

        self.success(data=query_result)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(
            article_id=ENFORCED,
            title=OPTIONAL,
            content=OPTIONAL,
            category_id=OPTIONAL)

        check_list = ('title', 'content', 'category_id')
        update_dict = dict(
            (arg, args.get(arg)) for arg in args.arguments if arg in check_list)

        update_result = tasks.update_article(
            article_id=args.article_id, **update_dict)

        self.success(data=update_result)

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = self.check_auth(2)
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

        self.success(data=insert_result)

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_form_arguments(
            article_id=ENFORCED)

        query_result = tasks.query_article(article_id=args.article_id)
        if not query_result:
            self.fail(4004)
        if query_result['user_id'] != _params.user_id:
            self.fail(4005)

        tasks.delete_article(article_id=args.article_id)

        self.success()


class ArticleId(BaseHandler):
    """Generate a id for article."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        self.success(data=dict(generate_id=generate_id()))


class ArticlePublishState(BaseHandler):
    """Generate a id for article."""

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_json_arguments(
            article_id=ENFORCED,
            publish_status=ENFORCED)

        _update_result = tasks.update_article_publish_state(
            article_id=args.article_id,
            publish_status=args.publish_status,)

        self.success()


class UserArticleList(BaseHandler):
    """Query Multi articles."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_form_arguments(
            category_id=ENFORCED,)

        query_result = tasks.query_article_info_list(
            user_id=_params.user_id,
            category_id=args.category_id)

        self.success(data=query_result)

class IndexArticleList(BaseHandler):
    """Query Multi articles."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):

        query_result = tasks.query_article_info_list()

        self.success(data=query_result)

ARTICLE_URLS = [
    (r'/article', Article),
    (r'/generate-id', ArticleId),
    (r'/article/user-list', UserArticleList),
    (r'/article/index-list', IndexArticleList),
    (r'/article/publish-state', ArticlePublishState)
]
