# coding:utf-8
"""Views module."""

from config import CFG as O_O

# from .account import ACCOUNT_URLS
# from .message import MESSAGE_URLS
from .user import USER_URLS

HANDLER_LIST = USER_URLS
# HANDLER_LIST = ACCOUNT_URLS
# HANDLER_LIST += MESSAGE_URLS
