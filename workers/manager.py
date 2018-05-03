# coding:utf-8
"""Module of celery task queue manager."""
import os
import traceback
from functools import wraps

from celery import Celery
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from lib.arguments import Arguments
from config import CFG as O_O, _ENV as env
from lib.logger import dump_in, dump_out, dump_error

DB_ENGINE = create_engine(
    O_O.database.mysql, echo=False, pool_recycle=100, encoding='utf-8')

SESS = sessionmaker(bind=DB_ENGINE)

QUEUE_LIST = None
APP = None

if O_O.celery.enabled:
    QUEUE_LIST = {
        'message': (5, 'gevent', 'info'),
        'db': (100, 'gevent', 'info'),
        'oss': (5, 'gevent', 'info'),
    }

    APP = Celery(
        'tasks',
        backend=O_O.celery.backend,
        broker=O_O.celery.broker,
    )

    APP.conf.update(
        task_serializer='json',
        result_serializer='json',
        result_expires=1800,
        task_default_queue='default',
        task_default_exchange='tasks',
        task_default_exchange_type='topic',
        task_default_routing_key='task.default',
        task_routes={
            f'workers.task_{q}.*': {
                'queue': f'{env}_{q}'
            }
            for q in QUEUE_LIST
        })


def exc_handler(function):
    """Wrap a handle shell to a query function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Function that wrapped."""
        session = SESS()
        try:
            res = function(sess=session, *args, **kwargs)
        except exc.IntegrityError as exception:
            res = dict(status=1, msg=str(exception.orig))
        except exc.ProgrammingError as exception:
            res = dict(status=2, msg=str(exception.orig))
        except exc.ResourceClosedError as exception:
            res = dict(status=3, msg=str(exception))
        except exc.OperationalError as exception:
            res = dict(status=4, msg=str(exception.orig))
        except UnicodeEncodeError as exception:
            res = dict(status=5, msg=str(exception))
        except:
            dump_error('my exception\n', traceback.format_exc())
            res = dict(status=255, msg='Unknown Error.')
        finally:
            session.close()

        if res and 'status' in res:
            return res
        else:
            return dict(status=0, data=res)

    return wrapper


class Tasks(Arguments):
    """Tasks Wrapper."""

    def __getattr__(self, name):
        return self[name]
