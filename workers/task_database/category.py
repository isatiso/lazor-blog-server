# coding:utf-8
"""Module of Table Category Query Function."""

import time
from hashlib import md5
from uuid import uuid1 as uuid
from sqlalchemy import desc

from models import Category
from workers.manager import exc_handler


@exc_handler
def query_category(category_id, **kwargs):
    """Query Category Info."""
    sess = kwargs.get('sess')

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
def query_category_by_user_id(user_id, **kwargs):
    """Query Category Info."""
    sess = kwargs.get('sess')

    category_list = sess.query(
        Category
    ).filter(
        Category.user_id == user_id
    ).order_by(
        desc(Category.create_time)
    ).all()

    category_list = [category.to_dict() for category in category_list]

    return category_list


@exc_handler
def insert_category(category_name, user_id, category_type, **kwargs):
    """Insert Category."""
    sess = kwargs.get('sess')

    new_category = Category(
        category_id=str(uuid()),
        user_id=user_id,
        category_name=category_name,
        category_type=category_type,
        create_time=int(time.time()))

    sess.add(new_category)
    sess.commit()

    return dict(result=1, status=0, msg='Successfully.')


@exc_handler
def update_category_name(category_id, category_name, **kwargs):
    """Update title or content of an article."""
    sess = kwargs.get('sess')

    category = sess.query(Category).filter(
        Category.category_id == category_id
    ).update({Category.category_name: category_name})
    result = category
    sess.commit()
    res = dict(result=1, status=0, msg='Successfully.', update=result)

    return res


@exc_handler
def delete_category(category_id, **kwargs):
    """Delete a category."""
    sess = kwargs.get('sess')

    if category_id == 'default':
        return None

    _category = sess.query(Category).filter(
        Category.category_id == category_id
    ).delete()
    sess.commit()

    res = dict(result=1, status=0, msg='Successfully.')
    return res


TASK_DICT = dict(
    query_category=query_category,
    update_category_name=update_category_name,
    query_category_by_user_id=query_category_by_user_id,
    insert_category=insert_category,
    delete_category=delete_category
)
