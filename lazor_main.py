#!/usr/local/bin/python3
# coding:utf-8
"""Main module of eSignDB."""
import os
import sys
import json

from tornado import gen, httpserver, ioloop, web

from base_handler import BaseHandler
from config import CFG as config
from views import HANDLER_LIST


class IndexHandler(BaseHandler):
    """Test index request handler."""

    @web.asynchronous
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        """Get method of IndexHandler."""
        self.render('index.html')


class TextHandler(BaseHandler):
    """Test index request handler."""

    def get(self, *_args, **_kwargs):
        """Handle some content file."""
        self.render('api.html')


class TestHandler(BaseHandler):
    """Test method."""

    def get(self, *_args, **_kwargs):
        """Test GET."""
        res = dict(method='GET', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    def post(self, *_args, **_kwargs):
        """Test POST."""
        res = dict(method='POST', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    def put(self, *_args, **_kwargs):
        """Test PUT."""
        res = dict(method='PUT', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    def delete(self, *_args, **_kwargs):
        """Test DELETE."""
        res = dict(method='DELETE', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)


class ServiceWorkerHandler(BaseHandler):
    """Test method."""

    def get(self, *_args, **kwargs):
        """Test GET."""
        self.set_header("Content-Type", "application/javascript")
        with open(
            '../wcd-ui/src/assets/js/service-worker.js', 'rb'
        ) as sw_file:
            self.finish(sw_file.read())


def main():
    """Esign DB program main function."""

    handlers = [
        (r'/', IndexHandler),
        (r'/text', TextHandler),
        (r'/back/api/explain', TextHandler),
        (r'/test(?P<path>.*)?', TestHandler),
        (r'/service-worker.js', ServiceWorkerHandler),
    ]

    handlers += [(f'/middle{handler[0]}', handler[1])
                 for handler in HANDLER_LIST]
    # handlers += PAY_URLS

    tornado_app = web.Application(
        handlers=handlers,
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        cookie_secret='QiNDQXm6ReOfl1VOGhdLoZ0f3ZucyEg6psGNLu1tWZE=', )

    tornado_server = httpserver.HTTPServer(
        tornado_app,
        xheaders=True, )

    # if options.port == 0:
    #     options.port = config.server.port
    # else:
    #     config.server.port = options.port

    tornado_server.listen(config.server.port)
    print('start listen...')
    sys.stdout.write('\nconfig:\n')
    json.dump(config.traverse(), sys.stdout, indent=4, sort_keys=True)
    sys.stdout.write('\n\n\n')
    sys.stdout.flush()

    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
