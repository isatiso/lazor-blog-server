# coding:utf-8
"""Views' Module of Article."""
import re
import os
from uuid import uuid1 as uuid
import time
from hashlib import md5, sha1
from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler, ENFORCED, OPTIONAL
from utils.utils import generate_id
from config import CFG as config
from workers.task_database import TASKS as tasks
from lib.qcos.bucket import Bucket

qcos_bucket = Bucket(
    bucket=config.cos.bucket,
    access_id=config.cos.access_id,
    access_key=config.cos.access_key,
    region=config.cos.region,
    appid=config.cos.appid)


class File(BaseHandler):
    """Handler file stuff."""

    # @asynchronous
    # @coroutine
    # def get(self, *_args, **_kwargs):
    #     args = self.parse_form_arguments(article_id=ENFORCED)

    #     query_result = tasks.query_article(article_id=args.article_id)

    #     self.success(data=query_result)

    # @asynchronous
    # @coroutine
    # def post(self, *_args, **_kwargs):
    #     _params = self.check_auth(2)
    #     if not _params:
    #         return

    #     args = self.parse_json_arguments(
    #         article_id=ENFORCED,
    #         title=OPTIONAL,
    #         content=OPTIONAL,
    #         category_id=OPTIONAL)

    #     check_list = ('title', 'content', 'category_id')
    #     update_dict = dict(
    #         (arg, args.get(arg)) for arg in args.arguments if arg in check_list)

    #     update_result = tasks.update_article(
    #         article_id=args.article_id, **update_dict)

    #     self.success(data=update_result)

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        file_meta = self.request.files
        file_list = []
        for fp in file_meta['file']:
            filename, ext = os.path.splitext(fp['filename'])

            ext = ext.lower()
            image_id = str(uuid())
            md5_code = md5(fp['body']).hexdigest()
            sha1_code = sha1(fp['body']).hexdigest()

            exist = self.image.find_one({
                'md5_code': md5_code,
                'sha1_code': sha1_code
            })
            if exist:
                file_list.append(
                    dict(
                        image_id=exist.get('image_id'),
                        path=exist.get('path'),
                        name=filename + ext))
                continue

            qcos_bucket.put_object(
                path='/image/' + image_id + ext.lower(), body=fp['body'])

            self.image.insert(
                dict(
                    image_id=image_id,
                    user_id=_params.user_id,
                    md5_code=md5_code,
                    sha1_code=sha1_code,
                    name=filename + ext,
                    path='/image/' + image_id + ext,
                    update_time=int(time.time())))

            file_list.append(
                dict(
                    image_id=image_id,
                    path='/image/' + image_id + ext,
                    name=filename + ext))

        self.success(data=dict(file_list=file_list))


class Image(BaseHandler):
    """Handler image stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        image_list = self.image.find(
            dict(user_id=_params.user_id),
            projection={
                '_id': 0,
                'md5_code': 0,
                'sha1_code': 0,
                'user_id': 0
            })

        res = list(image for image in image_list)
        self.success(data=res)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        pass

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        file_meta = self.request.files
        file_list = []
        for fp in file_meta['file']:
            filename, ext = os.path.splitext(fp['filename'])

            ext = ext.lower()
            image_id = str(uuid())
            md5_code = md5(fp['body']).hexdigest()
            sha1_code = sha1(fp['body']).hexdigest()

            exist = self.image.find_one({
                'md5_code': md5_code,
                'sha1_code': sha1_code
            })
            if exist:
                if 'user_id' not in exist:
                    self.image.update_one({
                        'md5_code': md5_code,
                        'sha1_code': sha1_code
                    }, {
                        '$set': {
                            'user_id': _params.user_id,
                            'update_time': int(time.time()),
                            'name': filename + ext
                        }
                    })
                file_list.append(
                    dict(
                        image_id=exist.get('image_id'),
                        path=exist.get('path'),
                        name=filename + ext))
                continue

            qcos_bucket.put_object(
                path=f'/image/' + image_id + ext.lower(), body=fp['body'])

            self.image.insert(
                dict(
                    image_id=image_id,
                    md5_code=md5_code,
                    sha1_code=sha1_code,
                    name=filename + ext,
                    path=f'/middle/image/record/' + image_id + ext,
                    update_time=int(time.time())))

            file_list.append(
                dict(
                    image_id=image_id,
                    path=f'/middle/image/record/' + image_id + ext,
                    name=filename + ext))

        self.success(data=dict(file_list=file_list))

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        _params = self.check_auth(2)
        if not _params:
            return

        args = self.parse_form_arguments(image_id=ENFORCED)

        image_info = self.image.find_one_and_delete(
            dict(image_id=args.image_id))

        if not image_info:
            self.fail(4004)

        qcos_bucket.delete_object(path=image_info['path'])

        self.success()


class ImageRecord(BaseHandler):
    """Handler image stuff."""

    id_checker = re.compile(
        r'^([0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})$')
    referer_checker = re.compile(r'\/\/lazor\.cn\/')

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        source = self.request.uri.split('/')[-1]
        referer = self.request.headers.get('Referer')

        if not referer or not re.search(self.referer_checker, referer):
            self.set_status(404)
            return self.fail(4004)

        image_id, ext = os.path.splitext(source)

        if re.match(self.id_checker, image_id):
            self.image.find_one_and_update({
                'image_id': image_id
            }, {
                '$set': {
                    'update_time': int(time.time())
                }
            })

        self.redirect('/image/' + source)


FILE_URLS = [
    (r'/file', File),
    (r'/image', Image),
    (r'/image/record/.*', ImageRecord),
]
