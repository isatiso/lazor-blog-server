# coding:utf-8
"""Predefination of mongo schema."""

from pymongo import MongoClient

from config import CFG as config

M_CLIENT = MongoClient(config.mongo.client).__getattr__(config.mongo.db)

MESSAGE_LIST = M_CLIENT.message_list
MESSAGE_LIST.create_index('user_id')
MESSAGE_LIST.ensure_index("date", expireAfterSeconds=3600 * 24)

LAZOR_USER = M_CLIENT.lazor_user
LAZOR_USER.create_index('user_id')
LAZOR_USER.create_index('username')
LAZOR_USER.create_index('create_time')

SESSION = M_CLIENT.session
