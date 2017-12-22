# coding:utf-8
"""Predefination of mongo schema."""

from pymongo import MongoClient

from config import CFG as config

M_CLIENT = MongoClient(config.mongo.client).__getattr__(config.mongo.db)

SESSION = M_CLIENT.session

ARTICLE_CONTENT = M_CLIENT.article_content
ARTICLE_CONTENT.create_index('article_id')

CATEGORY_ORDER = M_CLIENT.category_order
CATEGORY_ORDER.create_index('user_id')

ARTICLE_ORDER = M_CLIENT.article_order
ARTICLE_ORDER.create_index('category_id')
