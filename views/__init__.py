# coding:utf-8
"""Views module."""

from config import CFG as O_O

# from .account import ACCOUNT_URLS
# from .message import MESSAGE_URLS
from .user import USER_URLS
from .article import ARTICLE_URLS
from .category import CATEGORY_URLS
from .guard import GUARD_URLS
from .file import FILE_URLS

HANDLER_LIST = USER_URLS
HANDLER_LIST += ARTICLE_URLS
HANDLER_LIST += CATEGORY_URLS
HANDLER_LIST += GUARD_URLS
HANDLER_LIST += FILE_URLS
# HANDLER_LIST = ACCOUNT_URLS
# HANDLER_LIST += MESSAGE_URLS
