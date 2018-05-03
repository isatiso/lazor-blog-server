# coding:utf-8
"""Handlers."""
import time
from tornado import web, gen

from base_handler import BaseHandler

from config import CFG as O_O


class Index(BaseHandler):
    """Test index request handler."""

    @web.asynchronous
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        """Get method of IndexHandler."""
        self.render('index.html')


class Text(BaseHandler):
    """Test index request handler."""

    def get(self, *_args, **_kwargs):
        """Handle some content file."""
        self.render('api.html')


class Test(BaseHandler):
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


class ServiceWorker(BaseHandler):
    """Test method."""

    def get(self, *_args, **kwargs):
        """Test GET."""
        self.set_header("Content-Type", "application/javascript")
        with open('../wcd-ui/src/assets/js/service-worker.js',
                  'rb') as sw_file:
            self.finish(sw_file.read())


class Image(BaseHandler):
    """Test method."""

    def get(self, image_id, image_type, *_args, **kwargs):
        """Test GET."""
        if image_type == '.jpg':
            self.set_header("Content-Type", "image/jpeg")
        elif image_type == '.png':
            self.set_header("Content-Type", "image/png")
        elif image_type == '.gif':
            self.set_header("Content-Type", "image/GIF")

        try:
            with open('../static/image/' + image_id + image_type,
                      'rb') as sw_file:
                self.finish(sw_file.read())
        except FileNotFoundError:
            self.set_status(404)
            self.finish('404 File Not Found')
