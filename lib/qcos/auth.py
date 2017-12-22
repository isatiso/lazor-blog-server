# coding: utf-8
"""Auth Module."""

import hmac
import logging
import re
import time
from hashlib import sha1
from urllib import parse

from requests.auth import AuthBase

logger = logging.getLogger(__name__)


class Auth(AuthBase):
    """Auth"""

    def __init__(self, access_id, access_key, path=None, **kwargs):
        self._access_id = access_id
        self._access_key = access_key
        self._path = '/' + path.lstrip('/') if path else '/'
        self._expire = kwargs.get('expire', 10000)
        self._params = kwargs.get('params') or {}
        self.headers_pattern = re.compile(r'^(Content-Type|Host|[xX].*)$')

    def __call__(self, req):
        """
        reserved keywords in headers urlencode are -_.~,
        notice that / should be encoded and space should not be encoded to plus sign(+)
        """
        headers = self._filter_headers(req.headers)

        sign_time, msg = self._render_message(req.method, headers)

        signature = self._sign(sign_time, msg)

        req.headers['Authorization'] = self._re_assemble_headers(
            sign_time, headers, signature)

        return req

    def _filter_headers(self, data):
        """只设置host content-type 还有x开头的头部.

        :param data(dict): 所有的头部信息.
        :return(dict): 计算进签名的头部.
        """

        return {item.lower(): data[item] for item in data
                if re.match(self.headers_pattern, item) and data[item]}

    def _render_message(self, method, headers):
        format_str = '{method}\n{host}\n{params}\n{headers}\n'.format(
            method=method.lower(),
            host=self._path,
            params=parse.urlencode(sorted(self._params.items()), safe='-_.~'),
            headers=parse.urlencode(sorted(headers.items()), safe='-_.~')
        )

        now = int(time.time())
        sign_time = str(now - 60) + ';' + str(now + self._expire)

        msg = 'sha1\n{sign_time}\n{sha1}\n'.format(
            sign_time=sign_time,
            sha1=sha1(format_str.encode()).hexdigest())

        logger.debug('format str: %s', format_str)
        logger.debug('message to sign: %s', msg)
        return (sign_time, msg)

    def _sign(self, sign_time, msg):
        sign_key = hmac.new(key=self._access_key.encode(),
                            msg=sign_time.encode(),
                            digestmod=sha1).hexdigest()

        sign = hmac.new(key=sign_key.encode(),
                        msg=msg.encode(),
                        digestmod=sha1).hexdigest()

        logger.debug('sign key: %s', sign_key)
        logger.debug('sign: ' + sign)

        return sign

    def _re_assemble_headers(self, sign_time, headers, sign):
        result = (
            'q-sign-algorithm=sha1&'
            'q-ak={ak}&'
            'q-sign-time={sign_time}&'
            'q-key-time={key_time}&'
            'q-header-list={headers}&'
            'q-url-param-list={params}&'
            'q-signature={sign}'
        ).format(
            ak=self._access_id,
            sign_time=sign_time,
            key_time=sign_time,
            params=';'.join(key.lower() for key in self._params),
            headers=';'.join(headers),
            sign=sign)

        logger.debug('request headers: %s', result)
        return result

    @staticmethod
    def laugh():
        """fill method."""
        print('23333333333333333')

    @staticmethod
    def cry():
        """fill method."""
        print('55555555555555555')


class AuthFactory:
    """保存秘钥, 生成相应的 Auth 实例."""

    def __init__(self, access_id, access_key):
        self.change_access(access_id, access_key)

    def __call__(self, path='/', **kwargs):
        """生成一个 Auth 实例."""
        return Auth(self.access_id, self.access_key, path, **kwargs)

    def change_access(self, access_id, access_key):
        """修改秘钥"""
        self.access_id = access_id
        self.access_key = access_key

    @staticmethod
    def laugh():
        """fill method."""
        print('23333333333333333')

    @staticmethod
    def cry():
        """fill method."""
        print('55555555555555555')
