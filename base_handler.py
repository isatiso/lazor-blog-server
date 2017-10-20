# coding:utf-8
"""Base module for other views' modules."""
import json
import sys
import re
import time

from tornado import gen, httpclient
from tornado.web import HTTPError, MissingArgumentError, RequestHandler
from models import m_client
from config import CFG as config

STATUS_DICT = dict([
    # Normal Error
    (3001, 'Username or password is invalid'),
    (3002, 'Account is inactivated.'),
    (3003, 'Email not Register'),
    (3004, 'User name or email already exists.'),
    (3005, 'User\'s session key not exists, need to login.'),
    (3006, 'User\'s session value not exists, need to login'),
    (3007, 'Other people login this account, session is invalid.'),
    (3008, 'User Permission Deny.'),
    (3011, 'Account is not exists, please sign up.'),
    (3012, 'Address is not allowed.'),
    (3014, 'Nick Name already set.'),
    (3015, 'Either "nickname" or "password" should be in arguments.'),
    (3016, 'Either "username" or "email" should be in arguments.'),
    (3031, 'Not Regular Password'),
    (3032, 'Not Regular Email'),
    (3033, 'Not Regular Nickname'),
    (3100, 'Permission Deny.'),
    (3104, 'Chat Not Exists.'),
    (3105, 'Can not enter this chat.'),
    (3106, 'Chat owner missed.'),
    (3150, 'Chat Member Exists.'),
    (3151, 'Chat Member Not Exists.'),
    (3152, 'No Message Found.'),
])

ENFORCED = True
OPTIONAL = False


def underline_to_camel(underline_format):
    """Turn a underline format string to a camel format string."""
    pattern = re.split(r'_', underline_format)
    for i in range(1, len(pattern)):
        pattern[i] = pattern[i].capitalize()
    return ''.join(pattern)


def camel_to_underline(camel_format):
    """Turn a camel format string to a underline format string."""
    pattern = re.split(r'([A-Z])', camel_format)
    result = pattern[:1]
    result += [
        pattern[i].lower() + pattern[i + 1].lower()
        for i in range(1, len(pattern), 2)
    ]
    return '_'.join(result)


class Arguments(object):
    """Class to manage arguments of a requests."""

    def __init__(self, params):
        if isinstance(params, dict):
            self.arguments = params
        else:
            raise TypeError(
                f"Arguments data should be a 'dict' not {type(params)}.")

    def __getattr__(self, name):
        attr = self.arguments.get(name)
        if isinstance(attr, dict):
            attr = Arguments(attr)
        return attr

    def __getitem__(self, name):
        attr = self.arguments.get(name)
        if attr is None:
            raise KeyError(name)
        else:
            return attr

    def as_dict(self):
        """Return all the arguments as a dictonary."""
        return self.arguments

    def add(self, key, value):
        """Add a variable to args."""
        self.arguments[key] = value

    def get(self, key, default):
        """Get a variable of args."""
        if self.arguments.get(key):
            return self.arguments[key]
        else:
            return default


class ParseJSONError(HTTPError):
    """Exception raised by `BaseHandler.parse_json`.

    This is a subclass of `HTTPError`, so if it is uncaught a 400 response
    code will be used instead of 500 (and a stack trace will not be logged).
    """

    def __init__(self, doc):
        super(ParseJSONError, self).__init__(
            400, 'ParseJSONError. Decode JSON data in request body failed.')
        self.doc = doc


class BaseHandler(RequestHandler):
    """Custom handler for other views module."""
    session = m_client.session
    wcd_user = m_client.wcd_user
    message_list = m_client.message_list
    chat_list = m_client.chat_list
    pattern = dict(
        email=re.compile(r'^([\w-]+)@([\w-]+)(\.([\w-]+))+$'),
        password=re.compile(
            r'^[0-9A-Za-z`~!@#$%^&*()_+\-=\{\}\[\]:;"\'<>,.\\|?/]{6,24}$')
    )

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
    # Rewrite abstract method

    @gen.coroutine
    def get(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def put(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def delete(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def head(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def options(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def patch(self, *args, **kwargs):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def data_received(self, chunk):
        self.write('405: Method Not Allowed')

    @gen.coroutine
    def fetch(self, interface,
              method='GET', body=None, headers=None, **_kwargs):
        """Fetch Info from backend."""
        url = f'http://{config.server.back_ip}{interface}'
        _headers = dict(host=config.domain.root)
        if headers:
            _headers.update(headers)

        if not body:
            body = dict()
        back_info = yield httpclient.AsyncHTTPClient().fetch(
            url,
            method=method,
            headers=_headers,
            body=json.dumps(body),
            raise_error=False,
            allow_nonstandard_methods=True, )

        res = dict(
            http_code=back_info.code,
            res_body=back_info.body.decode() if back_info.body else None,
            interface=interface)

        if back_info.code >= 400:
            return Arguments(res)
        try:
            info = json.loads(res['res_body'])
            res.update(info)
        except json.JSONDecodeError:
            print(res['res_body'])

        return Arguments(res)

    def try_to_get_arg(self, name, default=None):
        """Get argument of specify key,
        if not exists ,return default value."""
        try:
            return self.get_argument(name)
        except MissingArgumentError:
            return default

    def get_current_user(self):
        """Get the current user from cookie."""
        user_id = self.get_secure_cookie('uoo')
        if isinstance(user_id, bytes):
            user_id = user_id.decode()
        return user_id

    def set_current_user(self, user_id=''):
        """Set current user to cookie."""
        self.set_secure_cookie(
            'uoo',
            user_id,
            expires=time.time() + config.server.expire_time,
            domain=self.request.host
        )

    def get_parameters(self):
        """Get user information from cookie."""
        params = self.get_secure_cookie('poo')
        params = json.loads(params.decode()) if params else dict()
        return Arguments(params)

    def set_parameters(self, params='', expire_time=3600):
        """Set user information to the cookie."""
        if isinstance(params, dict):
            params = json.dumps(params)
        self.set_secure_cookie(
            'poo',
            params,
            expires=time.time() + expire_time,
            domain=self.request.host
        )
        self.params = params
        return True

    def check_auth(self, check_level=1):
        """Check user status."""
        user_id = self.get_current_user()
        params = self.get_parameters()

        if not user_id or not params:
            self.set_current_user('')
            self.set_parameters({})
            self.dump_fail_data(3005)
            return False

        if check_level is 1:
            self.set_current_user(self.get_current_user())
            self.set_parameters(self.get_parameters().arguments)
            return params

        if not params.user_ip:
            self.set_current_user('')
            self.set_parameters({})
            self.dump_fail_data(3006)
            return False

        elif check_level is 2:
            self.set_current_user(self.get_current_user())
            self.set_parameters(self.get_parameters().arguments)
            return params

        sess_info = self.wcd_user.find_one({'user_ip': self.request.remote_ip})
        if sess_info:
            ac_code = sess_info.get('ac_code')
        else:
            ac_code = None
        if not params.ac_code or not ac_code or params.ac_code != ac_code:
            self.set_current_user('')
            self.set_parameters({})
            self.dump_fail_data(3007)
            return False
        elif check_level is 3:
            self.set_current_user(self.get_current_user())
            self.set_parameters(self.get_parameters().arguments)
            return params

        # role = params.get('role')
        # if role != 'normal':
        #     self.set_current_user('')
        #     self.set_parameters({})
        #     self.dump_fail_data(3008)
        #     return False
        # elif check_level is 4:
        #     self.set_current_user(self.get_current_user())
        #     self.set_parameters(self.get_parameters().arguments)
        #     return params

        # self.set_current_user(self.get_current_user())
        # self.set_parameters(self.get_parameters().arguments)
        return params

    def dump_fail_data(self, status,
                       back_data=None, data=None, polyfill=None, **_kwargs):
        """assemble and return error data."""
        if status in STATUS_DICT:
            msg = STATUS_DICT[status]
        else:
            print(status)
            raise KeyError(
                'Given status code is not in the status dictionary.')

        if polyfill:
            msg %= polyfill
        res = dict(
            result=0,
            status=status,
            msg=msg,
            data=data,
            back_data=back_data,
            **_kwargs)
        self.finish_with_json(res)
        return

    def fail(self, status, data=None, polyfill=None, **_kwargs):
        """assemble and return error data."""
        if status in STATUS_DICT:
            msg = STATUS_DICT[status]
        else:
            print(status)
            raise KeyError(
                'Given status code is not in the status dictionary.')

        if polyfill:
            msg %= polyfill
        res = dict(
            result=0,
            status=status,
            msg=msg,
            data=data,
            **_kwargs)
        self.finish_with_json(res)
        return

    def success(self, msg='Successfully.', data=None, **_kwargs):
        """assemble and return error data."""
        res = dict(
            result=1,
            status=0,
            msg=msg,
            data=data)
        self.finish_with_json(res)

    def parse_form_arguments(self, **keys):
        """Parse FORM argument like `get_argument`."""
        if config.debug:
            sys.stdout.write('\n\n' + '>' * 80)
            sys.stdout.write('\n' + (f'Input: '
                                     f'{self.request.method} '
                                     f'{self.request.path}') + '\n\n')
            sys.stdout.write(self.request.body.decode()[:500])
            sys.stdout.write('\n\n' + '>' * 80 + '\n')
            sys.stdout.flush()

        req = dict()

        for key in keys:
            try:
                req[key] = self.get_argument(key)
            except MissingArgumentError as exception:
                if keys[key] is ENFORCED:
                    raise exception
                elif keys[key] is OPTIONAL:
                    pass

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def parse_json_arguments(self, **keys):
        """Parse JSON argument like `get_argument`."""
        try:
            if config.debug:
                sys.stdout.write('\n\n' + '>' * 80)
                sys.stdout.write('\n' + (f'Input: '
                                         f'{self.request.method} '
                                         f'{self.request.path}') + '\n\n')
                sys.stdout.write(self.request.body.decode()[:500])
                sys.stdout.write('\n\n' + '>' * 80 + '\n')
                sys.stdout.flush()
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError as exception:
            # self.dump_fail_data(
            #     exc_doc=exception.doc, msg=exception.args[0], status=1)
            sys.stdout.write(self.request.body.decode())
            sys.stdout.write('\n')
            sys.stdout.flush()
            raise ParseJSONError(exception.doc)

        if not isinstance(req, dict):
            sys.stdout.write(self.request.body.decode())
            sys.stdout.write('\n')
            sys.stdout.flush()
            raise ParseJSONError('Req should be a dictonary.')

        for key in keys:
            if keys[key] is ENFORCED and key not in req:
                sys.stdout.write(self.request.body.decode())
                sys.stdout.write('\n')
                sys.stdout.flush()
                raise MissingArgumentError(key)

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def finish_with_json(self, data):
        """Turn data to JSON format before finish."""
        if config.debug:
            sys.stdout.write('' + '-' * 80)
            sys.stdout.write('\n' + (f'Output: '
                                     f'{self.request.method} '
                                     f'{self.request.path}') + '\n\n')
            sys.stdout.write(str(data))
            sys.stdout.write('\n\n' + '-' * 80 + '\n\n')
            sys.stdout.flush()
        self.finish(json.dumps(data).encode())

    def write_with_json(self, data):
        """Turn data to JSON format before write."""
        self.write(json.dumps(data).encode())

    def pattern_match(self, pattern_name, string):
        """Check given string."""
        return re.match(self.pattern[pattern_name], string)
