# coding:utf-8
"""Module of Table Article Query Function."""
import time
from uuid import uuid1 as uuid

from sqlalchemy import desc

from models import Article, User, Category
from workers.manager import exc_handler


@exc_handler
def query_article(article_id, **kwargs):
    """Query Article Info."""
    sess = kwargs.get('sess')

    article = sess.query(
        Article.article_id,
        Article.category_id,
        Article.user_id,
        Article.title,
        Article.content,
        Article.update_time,
        Article.create_time,
        Article.publish_status,
        User.username,
        User.email,
        Category.category_name,
        Category.category_type
    ).join(
        Category, Category.category_id == Article.category_id
    ).join(
        User, User.user_id == Article.user_id
    ).filter(
        Article.article_id == article_id
    ).first()

    head_list = [
        'article_id',
        'category_id',
        'user_id',
        'title',
        'content',
        'update_time',
        'create_time',
        'publish_status',
        'username',
        'email',
        'category_name',
        'category_type']

    if article:
        result = article = dict(zip(head_list, article))
    else:
        result = None

    return result


@exc_handler
def query_article_info_list(**kwargs):
    """Query Article Info."""
    sess = kwargs.get('sess')

    user_id = kwargs.get('user_id')
    category_id = kwargs.get('category_id')
    publish_status = kwargs.get('publish_status')
    limit = kwargs.get('limit')

    article_list = sess.query(
        Article.article_id,
        Article.category_id,
        Article.user_id,
        Article.title,
        Article.update_time,
        Article.create_time,
        Article.publish_status,
        Category.category_name,
        User.username
    ).join(
        Category, Category.category_id == Article.category_id
    ).join(
        User, User.user_id == Article.user_id
    )

    if user_id:
        article_list = article_list.filter(
            Article.user_id == user_id)

    if category_id:
        article_list = article_list.filter(
            Article.category_id == category_id)

    if publish_status:
        article_list = article_list.filter(
            Article.publish_status == publish_status)

    article_list = article_list.order_by(
        desc(Article.create_time)
    )

    if limit:
        article_list = article_list.limit(limit)
    else:
        article_list = article_list.all()

    head_list = [
        'article_id',
        'category_id',
        'user_id',
        'title',
        'update_time',
        'create_time',
        'publish_status',
        'category_name',
        'user_name']

    article_list = [
        dict(zip(head_list, article)) for article in article_list]

    return article_list


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

    result = new_article.to_dict()
    sess.add(new_article)
    sess.commit()

    return result


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


@exc_handler
def update_article_publish_state(article_id, publish_status, **kwargs):
    """Update publish state of an article."""
    sess = kwargs.get('sess')

    article = sess.query(Article).filter(
        Article.article_id == article_id
    ).update({
        Article.publish_status: publish_status
    })

    result = article
    sess.commit()

    return result


@exc_handler
def update_article_category_by_user_id(user_id, category_id, **kwargs):
    """Update category of an article."""
    sess = kwargs.get('sess')

    article = sess.query(Article).filter(
        Article.user_id == user_id
    ).filter(
        Article.category_id == category_id
    ).update({
        Article.category_id: 'default'
    })

    result = article
    sess.commit()

    return result


@exc_handler
def delete_article(article_id, **kwargs):
    """Delete article."""
    sess = kwargs.get('sess')

    sess.query(Article).filter(
        Article.article_id == article_id
    ).delete()

    sess.commit()

    return dict(result=1, status=0, data=None)


TASK_DICT = dict(
    query_article=query_article,
    query_article_info_list=query_article_info_list,
    insert_article=insert_article,
    update_article=update_article,
    update_article_publish_state=update_article_publish_state,
    update_article_category_by_user_id=update_article_category_by_user_id,
    delete_article=delete_article,
)
