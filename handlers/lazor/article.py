# coding:utf-8
"""Views' Module of Article."""
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from lib.generate import generate_id
from workers.task_db import TASKS as tasks


class Article(BaseHandler):
    """Handler article stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('article_id')

        query_result = tasks.query_article(article_id=args.article_id)
        if not query_result:
            self.fail(4004)

        article_content = self.article_content.find_one(
            dict(article_id=args.article_id))

        self.success(
            data=dict(query_result, content=article_content['content']))

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        _params = yield self.check_auth()

        args = self.parse_json_arguments(
            'article_id', title=None, content=None, category_id=None)

        if args.title or args.category_id:
            check_list = ('title', 'category_id')
            update_dict = dict((arg, args.get(arg)) for arg in args.arguments
                               if arg in check_list)

            update_result = tasks.update_article(
                article_id=args.article_id, **update_dict)
            if not update_result['result']:
                self.fail(5003)

        if args.content:
            update_result = self.article_content.update_one(
                {
                    'article_id': args.article_id
                }, {'$set': {
                    'content': args.content
                }},
                upsert=True)
            if not update_result:
                self.fail(5003)

        query_result = tasks.query_article(article_id=args.article_id)

        self.success(data=dict(query_result, content=args.content))

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = yield self.check_auth()

        args = self.parse_json_arguments('category_id')

        insert_result = tasks.insert_article(
            user_id=_params.user_id,
            title='无标题文章',
            content='',
            category_id=args.category_id)

        self.article_content.update_one(
            dict(article_id=insert_result['data']['article_id']),
            {'$set': {
                'content': ''
            }},
            upsert=True)

        self.success(data=dict(insert_result['data']))

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        _params = yield self.check_auth()

        args = self.parse_form_arguments('article_id')

        query_result = tasks.query_article(article_id=args.article_id)
        if not query_result:
            self.fail(4004)
        if query_result['user_id'] != _params.user_id:
            self.fail(4005)

        tasks.delete_article(article_id=args.article_id)
        self.article_content.delete_one({'article_id': args.article_id})

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
        _params = yield self.check_auth()

        args = self.parse_json_arguments('article_id', 'publish_status')

        _update_result = tasks.update_article_publish_state(
            article_id=args.article_id,
            publish_status=args.publish_status,
        )

        self.success()


class UserArticleList(BaseHandler):
    """Query Multi articles."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):

        args = self.parse_form_arguments('category_id')

        query_result = tasks.query_article_info_list(
            category_id=args.category_id)

        order_list = self.article_order.find_one({
            'category_id':
            args.category_id
        })

        if order_list:
            order_list = order_list.get('article_order')

        self.success(
            data=dict(article_list=query_result, order_list=order_list))


class IndexArticleList(BaseHandler):
    """Query Multi articles."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):

        args = self.parse_form_arguments('limit')

        query_result = tasks.query_article_info_list(limit=args.limit)

        self.success(data=dict(article_list=query_result, order_list=None))


class ArticleOrder(BaseHandler):
    """Handler category order stuff."""

    def post(self, *_args, **_kwargs):
        _params = yield self.check_auth()

        args = self.parse_json_arguments('category_id', 'order_list')

        self.article_order.update(
            {
                'category_id': args.category_id
            }, {'$set': {
                'article_order': args.order_list
            }},
            upsert=True)

        self.success()
