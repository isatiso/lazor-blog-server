# coding:utf-8
"""Predefination of mongo schema."""

from pymongo import MongoClient

from config import CFG as O_O

M_CLIENT = MongoClient(O_O.database.mongo.client).__getattr__(
    O_O.database.mongo.db)

SESSION = M_CLIENT.session

ARTICLE_CONTENT = M_CLIENT.article_content
ARTICLE_CONTENT.create_index('article_id')

CATEGORY_ORDER = M_CLIENT.category_order
CATEGORY_ORDER.create_index('user_id')

ARTICLE_ORDER = M_CLIENT.article_order
ARTICLE_ORDER.create_index('category_id')

IMAGE = M_CLIENT.image
IMAGE.create_index('image_id')
IMAGE.create_index('md5_code')
IMAGE.create_index('user_id')


class Mongo:
    """Mongo Client Set."""
    session = M_CLIENT.session
    category_order = M_CLIENT.category_order
    article_order = M_CLIENT.article_order
    article_content = M_CLIENT.article_content
    image = M_CLIENT.image
    access_log = M_CLIENT.access_log

    @staticmethod
    def laugh():
        """fill method."""
        print('23333333333333333')

    @staticmethod
    def cry():
        """fill method."""
        print('55555555555555555')
