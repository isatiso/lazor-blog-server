# coding:utf-8
"""Routes Module."""

from .index import INDEX_ROUTES
from .lazor import LAZOR_ROUTES

ROUTES = sum([INDEX_ROUTES, LAZOR_ROUTES], [])
