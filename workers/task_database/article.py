# coding:utf-8
"""Module of Table Article Query Function."""

import time
from hashlib import md5
from uuid import uuid1 as uuid

from models import Article
from workers.manager import exc_handler


@exc_handler
def query_article(article_id, **kwargs):
    """Query Article Info."""
    sess = kwargs.get('sess')

    article_id = kwargs.get('article_id')

    article = sess.query(
        Article
    ).filter(
        Article.article_id == article_id
    ).first()

    if article:
        result = article.to_dict()
    else:
        result = None

    return result


@exc_handler
def insert_article(title, content, user_id, category_id,
                   **kwargs):
    """Insert Article."""
    sess = kwargs.get('sess')

    new_article = Article(
        article_id=str(uuid()),
        category_id=category_id,
        user_id=user_id,
        title=title,
        content=content,
        publish_status=0,
        update_time=int(time.time()),
        create_time=int(time.time()),)

    sess.add(new_article)
    sess.commit()

    return dict(result=1, status=0, msg='Successfully.')


@exc_handler
def update_article(article_id, **kwargs):
    """Update title or content of an article."""
    sess = kwargs.get('sess')

    kwargs['update_time'] = int(time.time())

    invert_dict = dict(
        title=Article.title,
        content=Article.content,
        category_id=Article.category_id,
        update_time=Article.update_time
    )

    key_list = list(invert_dict.keys())
    for key in key_list:
        if key not in kwargs:
            del invert_dict[key]

    update_dict = dict([(invert_dict[k], kwargs[k]) for k in invert_dict])

    if update_dict:
        article = sess.query(Article).filter(
            Article.article_id == article_id
        ).update(update_dict)
        result = article
        sess.commit()
        res = dict(result=1, status=0, msg='Successfully.', update=result)
    else:
        res = dict(result=0, status=3, msg='Failure.')

    return res


TASK_DICT = dict(
    query_article=query_article,
    insert_article=insert_article,
    update_article=update_article
)
