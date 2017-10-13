# coding:utf-8
"""Module of Table Category Query Function."""

import time
from hashlib import md5
from uuid import uuid1 as uuid

from models import Category
from workers.manager import exc_handler


@exc_handler
def query_category(category_id, **kwargs):
    """Query Category Info."""
    sess = kwargs.get('sess')

    category_id = kwargs.get('category_id')

    category = sess.query(
        Category
    ).filter(
        Category.category_id == category_id
    ).first()

    if category:
        result = category.to_dict()
    else:
        result = None

    return result


@exc_handler
def insert_category(name, user_id, **kwargs):
    """Insert Category."""
    sess = kwargs.get('sess')

    new_category = Category(
        category_id=str(uuid()),
        user_id=user_id,
        name=name)

    sess.add(new_category)
    sess.commit()

    return dict(result=1, status=0, msg='Successfully.')


@exc_handler
def update_article_name(category_id, name, **kwargs):
    """Update title or content of an article."""
    sess = kwargs.get('sess')

    category = sess.query(Category).filter(
        Category.category_id == category_id
    ).update({Category.name: name})
    result = category
    sess.commit()
    res = dict(result=1, status=0, msg='Successfully.', update=result)

    return res


TASK_DICT = dict(
    query_category=query_category,
    update_article_name=update_article_name,
    insert_category=insert_category
)
