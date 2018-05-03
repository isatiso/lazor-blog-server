# coding:utf-8
"""Query Task of Database lazor_blog."""

from workers.manager import APP as app, Tasks
from workers.task_db.user import TASK_DICT as user_dict
from workers.task_db.article import TASK_DICT as article_dict
from workers.task_db.category import TASK_DICT as category_dict

TASK_DICT = dict()
TASK_DICT.update(user_dict)
TASK_DICT.update(article_dict)
TASK_DICT.update(category_dict)

TASKS = Tasks(TASK_DICT)
