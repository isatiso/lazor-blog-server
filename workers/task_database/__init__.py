# coding:utf-8
"""Query Task of Database lazor_blog."""
from workers import Tasks
from workers.task_database.user import TASK_DICT as user_dict
from workers.task_database.article import TASK_DICT as article_dict
from workers.task_database.category import TASK_DICT as category_dict


TASK_DICT = dict()
TASK_DICT.update(user_dict)
TASK_DICT.update(article_dict)
TASK_DICT.update(category_dict)

TASKS = Tasks(TASK_DICT)
