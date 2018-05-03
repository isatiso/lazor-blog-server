# coding:utf-8

from handlers import index

INDEX_ROUTES = [
    (r'/', index.Index),
    (r'/text', index.Text),
    (r'/back/api/explain', index.Text),
    (r'/test(?P<path>.*)?', index.Test),
    (r'/image/(?P<image_id>[a-zA-Z0-9\-]{36})(?P<image_type>.jpg|.png|.gif)',
     index.Image),
    (r'/service-worker.js', index.ServiceWorker),
]
