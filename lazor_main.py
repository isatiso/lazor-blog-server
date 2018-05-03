#!/usr/local/bin/python3
# coding:utf-8
"""Main module of eSignDB."""
import os
import sys
import json

from tornado import gen, httpserver, ioloop, web

from base_handler import BaseHandler
from config import CFG as O_O
from routes import ROUTES as routes


def main():
    """Esign DB program main function."""

    tornado_app = web.Application(handlers=routes, **O_O.application)
    tornado_server = httpserver.HTTPServer(tornado_app, **O_O.httpserver)

    tornado_server.listen(O_O.server.port)
    print('start listen...')
    O_O.show()

    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
