# coding:utf-8
"""Views module."""

from config import CFG as O_O

from .user import USER_URLS
from .article import ARTICLE_URLS
from .category import CATEGORY_URLS
from .guard import GUARD_URLS
from .file import FILE_URLS
from .log import LOG_URLS

HANDLER_LIST = USER_URLS
HANDLER_LIST += ARTICLE_URLS
HANDLER_LIST += CATEGORY_URLS
HANDLER_LIST += GUARD_URLS
HANDLER_LIST += FILE_URLS
HANDLER_LIST += LOG_URLS
