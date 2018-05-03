# coding:utf-8
"""Base module for other views' modules."""
import json
import re
import time

from tornado import gen, httpclient
from tornado.web import Finish, MissingArgumentError, RequestHandler
from models import Mongo
from config import get_status_message, CFG as O_O
from lib.arguments import Arguments
from lib.errors import ParseJSONError
from lib.logger import dump_in, dump_out, dump_error

ENFORCED = True
OPTIONAL = False


class BaseHandler(RequestHandler, Mongo):
    """Custom handler for other views module."""

    pattern = dict(
        email=re.compile(r'^([\w\-.]+)@([\w-]+)(\.([\w-]+))+$'),
        password=re.compile(
            r'^[0-9A-Za-z`~!@#$%^&*()_+\-=\{\}\[\]:;"\'<>,.\\|?/]{6,24}$'))

    # Set the public head here.
    # pub_head = dict(
    #     version='?v=20160301&t=' + str(time.time()),
    #     base_url=options.BASE_URL,
    #     base_static_url=options.BASE_STATIC_URL,
    #     base_resource_url=options.BASE_RESOURCE_URL,
    # )
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.params = None

    def get_current_user(self):
        """Get current user from cookie.
        p.s. self.get_secure_cookie 方法只会返回 None 或者 bytes."""
        user_id = self.get_secure_cookie(O_O.server.cookie_name.user_id)
        return user_id and user_id.decode()

    def set_current_user(self, user_id=''):
        """Set current user to cookie."""
        self.set_secure_cookie(
            name=O_O.server.cookie_name.user_id,
            value=user_id,
            expires=time.time() + O_O.server.expire_time,
            domain=self.request.host)

    def get_parameters(self):
        """Get user information from cookie."""
        params = self.get_secure_cookie(O_O.server.cookie_name.parameters)
        return Arguments(params and json.loads(params.decode()))

    def set_parameters(self, params=''):
        """Set user information to the cookie."""
        if not isinstance(params, dict):
            raise ValueError('params should be <class \'dict\'>')
        self.set_secure_cookie(
            name=O_O.server.cookie_name.parameters,
            value=json.dumps(params),
            expires=time.time() + O_O.server.expire_time,
            domain=self.request.host)

    @gen.coroutine
    def get_session_code(self):
        if O_O.database.mongo:
            sess_info = self.session.find_one({
                O_O.database.mongo.session_key:
                self.request.remote_ip
            })
            return sess_info and sess_info.get('session_code')

        return ''

    @gen.coroutine
    def set_session(self, session):
        pass

    @gen.coroutine
    def remove_session(self, session_id):
        pass

    def fail(self, status, data=None, polyfill=None, **_kwargs):
        """assemble and return error data."""
        msg = get_status_message(status)
        self.finish_with_json(
            dict(status=status, msg=msg, data=data, **_kwargs))

    def success(self, data=None, msg='Successfully.', **_kwargs):
        """assemble and return error data."""
        self.finish_with_json(dict(status=0, msg=msg, data=data))

    @gen.coroutine
    def fetch(self, api, method='GET', body=None, headers=None, **_kwargs):
        """Fetch Info from backend."""
        body = body or dict()

        _headers = dict(host=self.request.host)
        if headers:
            _headers.update(headers)

        if '://' not in api:
            api = f'http://{O_O.server.back_ip}{api}'

        back_info = yield httpclient.AsyncHTTPClient().fetch(
            api,
            method=method,
            headers=_headers,
            body=json.dumps(body),
            raise_error=False,
            allow_nonstandard_methods=True)

        res_body = back_info.body and back_info.body.decode() or None

        if back_info.code >= 400:
            return Arguments(
                dict(http_code=back_info.code, res_body=res_body, api=api))

        try:
            return Arguments(json.loads(res_body))
        except json.JSONDecodeError:
            pass

    def check_auth(self, **kwargs):
        """Check user status."""
        user_id = self.get_current_user()
        params = self.get_parameters()

        def clean_and_fail(code):
            self.set_current_user('')
            self.set_parameters({})
            self.fail(code)

        if not user_id or not params:
            clean_and_fail(3005)

        if user_id != params.id:
            clean_and_fail(3006)

        for key in kwargs:
            if params[key] != kwargs[key]:
                dump_error(f'Auth Key Error: {key}')
                self.fail(4003)

        # ac_code = yield self.get_session_code()
        # if ac_code is not '' and params.ac_code != ac_code:
        #     clean_and_fail(3007)

        self.set_current_user(self.get_current_user())
        self.set_parameters(self.get_parameters())
        return params

    def parse_form_arguments(self, *enforced_keys, **optional_keys):
        """Parse FORM argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',
                    self.request.body.decode()[:500])

        req = dict()
        for key in enforced_keys:
            req[key] = self.get_argument(key)
        for key in optional_keys:
            values = self.get_arguments(key)
            if len(values) is 0:
                req[key] = optional_keys.get(key)
            elif len(values) is 1:
                req[key] = values[0]
            else:
                req[key] = values

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def parse_json_arguments(self, *enforced_keys, **optional_keys):
        """Parse JSON argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',)
                    # self.request.body.decode('utf-8')[:500])

        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError as exception:
            dump_error(self.request.body.decode())
            raise ParseJSONError(exception.doc)

        if not isinstance(req, dict):
            dump_error(self.request.body.decode())
            raise ParseJSONError('Req should be a dictonary.')

        for key in enforced_keys:
            if key not in req:
                dump_error(self.request.body.decode())
                raise MissingArgumentError(key)

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def finish_with_json(self, data):
        """Turn data to JSON format before finish."""
        self.set_header('Content-Type', 'application/json')
        if O_O.debug:
            dump_out(f'Output: {self.request.method} {self.request.path}',
                     str(data['data']))

        raise Finish(json.dumps(data).encode())

    @gen.coroutine
    def wait(self, func, args=None, kwargs=None):
        """Method to waiting celery result."""
        async_task = func.apply_async(args=args, kwargs=kwargs)

        while True:
            if async_task.status in ['PENDING', 'PROGRESS']:
                yield gen.sleep(O_O.celery.sleep_time)
            elif async_task.status in ['SUCCESS', 'FAILURE']:
                break
            else:
                print('\n\nUnknown status:\n', async_task.status, '\n\n\n')
                break

        if async_task.status != 'SUCCESS':
            dump_error(f'Task Failed: {func.name}[{async_task.task_id}]',
                       f'    {str(async_task.result)}')
            result = dict(status=1, data=async_task.result)
        else:
            result = async_task.result

        if result.get('status'):
            self.fail(-1, result)
        else:
            return result

    def pattern_match(self, pattern_name, string):
        """Check given string."""
        return re.match(self.pattern[pattern_name], string)
