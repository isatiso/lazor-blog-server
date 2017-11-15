# coding:utf-8
"""Module of Table Account Query Function."""

import time
from hashlib import md5
from uuid import uuid1 as uuid

from models import User
from workers.manager import exc_handler


@exc_handler
def query_user(**kwargs):
    """Query User Info."""
    sess = kwargs.get('sess')

    email = kwargs.get('email')
    user_id = kwargs.get('user_id')
    username = kwargs.get('username')

    user = sess.query(User)

    if user_id:
        user = user.filter(User.user_id == user_id)
    elif email:
        user = user.filter(User.email == email)
    elif username:
        user = user.filter(User.username == username)
    else:
        return dict(
            result=0,
            status=1,
            msg=('Missing Argument, '
                 'either "user_id" or "email" should in arguments.'),
            data=None)

    user = user.first()

    if user:
        result = user.to_dict()
    else:
        result = None

    return result


@exc_handler
def query_username_exists(username, **kwargs):
    """Query username if exists."""
    sess = kwargs.get('sess')

    username_exists = sess.query(User).filter(
        User.username == username).first()

    return True if username_exists else False


@exc_handler
def query_email_exists(email, **kwargs):
    """Query email if exists."""
    sess = kwargs.get('sess')

    email_exists = sess.query(User).filter(User.email == email).first()

    return True if email_exists else False


@exc_handler
def query_email_or_username_exists(email, username, **kwargs):
    """Query email if exists."""
    sess = kwargs.get('sess')

    email_exists = sess.query(User).filter(User.email == email).first()
    username_exists = sess.query(User).filter(
        User.username == username).first()

    return True if email_exists or username_exists else False


@exc_handler
def insert_user(email, pswd, username, **kwargs):
    """Insert a user."""
    sess = kwargs.get('sess')

    new_user = User(
        user_id=str(uuid()),
        username=username,
        email=email,
        pswd=pswd,
        create_time=int(time.time()))

    result = new_user.to_dict()

    sess.add(new_user)
    sess.commit()

    return dict(result=1, status=0, msg='Successfully.', data=result)


@exc_handler
def update_user_name(user_id, username, **kwargs):
    """Insert a user."""
    sess = kwargs.get('sess')

    update_result = sess.query(User).filter(
        User.user_id == user_id
    ).update(
        {User.username: username})

    sess.commit()

    return dict(result=1, status=0, msg='Successfully.', data=update_result)

# @exc_handler
# def update_user_info(user_id, **kwargs):
#     """Update information of a user."""
#     sess = kwargs.get('sess')

#     email = kwargs.get('email')
#     user_id = kwargs.get('user_id')

#     user = sess.query(User)

#     if user_id:
#         user = user.filter(User.user_id == user_id)
#     elif email:
#         user = user.filter(User.email == email)
#     else:
#         return dict(
#             result=0,
#             status=1,
#             msg=('Missing Argument, '
#                  'either "user_id" or "email" should in arguments.'),
#             data=None)

#     invert_dict = dict(

#     )
#     pass

TASK_DICT = dict(
    insert_user=insert_user,
    query_user=query_user,
    query_username_exists=query_username_exists,
    query_email_exists=query_email_exists,
    query_email_or_username_exists=query_email_or_username_exists,
    update_user_name=update_user_name,
)
