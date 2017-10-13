# coding:utf-8
"""Module of celery task queue manager."""

import traceback
from functools import wraps

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from workers import env, O_O

DB_ENGINE = create_engine(
    O_O.mysql, echo=False, pool_recycle=100, encoding='utf-8')

SESS = sessionmaker(bind=DB_ENGINE)


def exc_handler(function):
    """Wrap a handle shell to a query function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Function that wrapped."""
        session = SESS()
        try:
            res = function(sess=session, *args, **kwargs)
        except exc.IntegrityError as exception:
            res = dict(result=0, status=1, msg=str(exception.orig))
        except exc.ProgrammingError as exception:
            res = dict(result=0, status=2, msg=str(exception.orig))
        except exc.ResourceClosedError as exception:
            res = dict(result=0, status=3, msg=str(exception))
        except exc.OperationalError as exception:
            res = dict(result=0, status=4, msg=str(exception.orig))
        except UnicodeEncodeError as exception:
            res = dict(result=0, status=5, msg=str(exception))
        except:
            print('my exception\n\n')
            traceback.print_exc()
            print('=' * 80, '\n\n')
            res = dict(result=0, status=255, msg='Unknown Error.')
        finally:
            session.close()

        return res

    return wrapper
