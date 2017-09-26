# coding:utf-8
"""Views' Module of Message."""
from hashlib import md5
from uuid import uuid1 as uuid
from datetime import datetime
import time

from pprint import pprint

from tornado.gen import coroutine
from tornado.web import asynchronous

from base_handler import BaseHandler


class ChatRoom(BaseHandler):
    """Handler message stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_form_arguments([], ['chat_id'])

        if not args.chat_id:
            chat_info = self.chat_list.find({'chat_create_time': {'$gt': 1}})
            chat_info = [chat for chat in chat_info]
            for chat in chat_info:
                if '_id' in chat:
                    del chat['_id']
        else:
            chat_info = self.chat_list.find_one({'chat_id': args.chat_id})
            if not chat_info:
                return self.dump_fail_data(3104)

            owner_info = self.wcd_user.find_one({
                'user_ip':
                chat_info['creator_ip']
            })
            if not owner_info:
                return self.dump_fail_data(3106)

            self.chat_list.update_one({
                'chat_id': args.chat_id
            }, {'$set': {
                'creator_nick': owner_info['nickname']
            }})

            member_list = chat_info['chat_member']
            member_detail = self.wcd_user.find({
                'user_ip': {
                    '$in': member_list
                }
            })

            member_list = [{
                'user_ip': member['user_ip'],
                'nickname': member['nickname'],
                'color': member['color']
            } for member in member_detail]

            chat_info['chat_member'] = member_list
            if '_id' in chat_info:
                del chat_info['_id']

        res = dict(result=1, status=0, msg='Successfully.', data=chat_info)
        self.finish_with_json(res)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_json_arguments(['chat_name'])

        chat_info = dict(
            chat_id=str(uuid()),
            chat_name=args.chat_name,
            creator_ip=_params.user_ip,
            creator_nick=_params.nickname,
            chat_secret=args.chat_secret,
            chat_create_time=int(time.time()),
            chat_member=[_params.user_ip], )
        self.chat_list.insert_one(chat_info)
        if '_id' in chat_info:
            del chat_info['_id']

        res = dict(result=1, status=0, msg='Successfully.', data=chat_info)
        self.finish_with_json(res)

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_form_arguments(['chat_id'])

        chat_info = self.chat_list.find_one(dict(chat_id=args.chat_id))
        if not chat_info:
            return self.dump_fail_data(3104)
        if chat_info['creator_ip'] != _params.user_ip:
            return self.dump_fail_data(3100)

        self.chat_list.delete_one(dict(chat_id=args.chat_id))

        res = dict(result=1, status=0, msg='Successfully.', data=None)
        self.finish_with_json(res)


class ChatMember(BaseHandler):
    """Handler message stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_form_arguments(['chat_id'])

        chat_list = self.chat_list.find_one({'chat_id': args.chat_id})

        if not chat_list:
            return self.dump_fail_data(3104)

        member_list = [member_ip for member_ip in chat_list['chat_member']]

        if _params.user_ip not in member_list:
            return self.dump_fail_data(3105)

        res = dict(result=1, status=0, msg='successfully.', data=None)
        self.finish_with_json(res)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        pass

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_json_arguments(['member_ip', 'chat_id'])

        user_info = self.wcd_user.find_one(dict(user_ip=args.member_ip))

        if not user_info:
            return self.dump_fail_data(3011)

        chat_info = self.chat_list.update_one(
            dict(chat_id=args.chat_id),
            {'$addToSet': {
                'chat_member': args.member_ip,
            }})

        res = dict(result=1, status=0, msg='Successfully.', data=None)
        self.finish_with_json(res)

    @asynchronous
    @coroutine
    def delete(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_form_arguments(['member_ip', 'chat_id'])

        user_info = self.wcd_user.find_one(dict(user_ip=args.member_ip))

        if not user_info:
            return self.dump_fail_data(3011)

        chat_info = self.chat_list.update_one(
            dict(chat_id=args.chat_id),
            {'$pull': {
                'chat_member': args.member_ip
            }})

        res = dict(result=1, status=0, msg='Successfully.', data=None)
        self.finish_with_json(res)


class Message(BaseHandler):
    """Handler message stuff."""

    @asynchronous
    @coroutine
    def get(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_form_arguments(['chat_id', 'start'])
        if not args.end:
            args.add('end', int(time.time() * 1000))

        query_dict = {
            'chat_id': args.chat_id,
            'msg_time': {
                '$gt': int(args.start),
                '$lte': int(args.end)
            }
        }

        msg_list = self.message_list.find(query_dict).sort('msg_time', -1)
        msg_list = msg_list.limit(30)

        msg_list = [msg for msg in msg_list]
        if not msg_list:
            return self.dump_fail_data(3152)

        last_msg_time = 0
        for msg in msg_list:
            if msg['msg_time'] > last_msg_time:
                last_msg_time = msg['msg_time']
            del msg['_id']
            del msg['date']

        res = dict(
            result=1,
            status=0,
            msg='message successfully.',
            data=dict(msg_list=msg_list, end_time=int(last_msg_time)))
        self.finish_with_json(res)

    @asynchronous
    @coroutine
    def post(self, *_args, **_kwargs):
        pass

    @asynchronous
    @coroutine
    def put(self, *_args, **_kwargs):
        res = self.check_auth(3)
        if not res:
            return
        else:
            _user_id, _params = res

        args = self.parse_json_arguments(['message', 'chat_id'])

        self.message_list.insert_one({
            'msg_id': uuid().hex,
            'message': args.message,
            'chat_id': args.chat_id,
            'msg_time': int(time.time() * 1000),
            'date': datetime.utcnow(),
            'nickname': _params.nickname,
            'user_ip': _params.user_ip
        })
        res = dict(result=1, status=0, msg='successfully.', data=None)
        self.finish_with_json(res)


MESSAGE_URLS = [
    (r'/message', Message),
    (r'/chat-list', ChatRoom),
    (r'/chat-member', ChatMember),
]
