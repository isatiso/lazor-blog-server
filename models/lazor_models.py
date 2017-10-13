# coding:utf-8
"""Lazor Database Module."""

from sqlalchemy import (CHAR, Column, Enum, Integer, SmallInteger, String,
                        Text, UniqueConstraint)

from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

BASE.to_dict = lambda self: dict(
    [
        (key, self.__dict__[key])
        for key in self.__dict__
        if not key.startswith('_')
    ])

BASE.__repr__ = lambda self: self.__tablename__ + ' => ' + str(self.to_dict())


class User(BASE):
    """User Model."""
    __tablename__ = 'user'

    user_id = Column(CHAR(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    pswd = Column(CHAR(32), nullable=False)
    create_time = Column(Integer, nullable=False, index=True)

    __table_args__ = ({'mysql_engine': 'InnoDB'}, )


class Article(BASE):
    """Article Model."""
    __tablename__ = 'article'

    article_id = Column(CHAR(36), primary_key=True)
    category_id = Column(CHAR(36), default='default', index=True)
    user_id = Column(CHAR(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    update_time = Column(Integer, nullable=False, index=True)
    create_time = Column(Integer, nullable=False, index=True)

    __table_args__ = ({'mysql_engine': 'InnoDB'}, )


class Category(BASE):
    """Category Model."""
    __tablename__ = 'category'

    category_id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    __table_args__ = ({'mysql_engine': 'InnoDB'}, )
