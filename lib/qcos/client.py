# coding=utf-8
"""COS Client Module."""

import base64
import logging
from hashlib import md5
from urllib import parse
from xml.dom import minidom

from dicttoxml import dicttoxml
from requests import session, Request

from .auth import AuthFactory
from .comm import XMLParser
from .exception import CosClientError, CosServiceError

logging.basicConfig(
    level=logging.INFO,
    format=
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='cos_v5.log',
    filemode='a')

logger = logging.getLogger(__name__)


class Config(object):
    """Config类，保存用户相关信息"""

    single_upload_length = 5 * 1024 * 1024  # 单次上传文件最大为5G
    _maplist = dict(
        ContentLength='Content-Length',
        ContentMD5='Content-MD5',
        ContentType='Content-Type',
        CacheControl='Cache-Control',
        ContentDisposition='Content-Disposition',
        ContentEncoding='Content-Encoding',
        ContentLanguage='Content-Language',
        Expires='Expires',
        ResponseContentType='response-content-type',
        ResponseContentLanguage='response-content-language',
        ResponseExpires='response-expires',
        ResponseCacheControl='response-cache-control',
        ResponseContentDisposition='response-content-disposition',
        ResponseContentEncoding='response-content-encoding',
        Metadata='Metadata',
        ACL='x-cos-acl',
        GrantFullControl='x-cos-grant-full-control',
        GrantWrite='x-cos-grant-write',
        GrantRead='x-cos-grant-read',
        StorageClass='x-cos-storage-class',
        Range='Range',
        IfMatch='If-Match',
        IfNoneMatch='If-None-Match',
        IfModifiedSince='If-Modified-Since',
        IfUnmodifiedSince='If-Unmodified-Since',
        CopySourceIfMatch='x-cos-copy-source-If-Match',
        CopySourceIfNoneMatch='x-cos-copy-source-If-None-Match',
        CopySourceIfModifiedSince='x-cos-copy-source-If-Modified-Since',
        CopySourceIfUnmodifiedSince='x-cos-copy-source-If-Unmodified-Since',
        VersionId='x-cos-version-id',
        content_length='Content-Length',
        content_md5='Content-MD5',
        content_type='Content-Type',
        cache_control='Cache-Control',
        content_disposition='Content-Disposition',
        content_encoding='Content-Encoding',
        content_language='Content-Language',
        expires='Expires',
        response_content_type='response-content-type',
        response_contentLanguage='response-content-language',
        response_expires='response-expires',
        response_cache_control='response-cache-control',
        response_content_disposition='response-content-disposition',
        response_content_encoding='response-content-encoding',
        metadata='Metadata',
        acl='x-cos-acl',
        grant_full_control='x-cos-grant-full-control',
        grant_write='x-cos-grant-write',
        grant_read='x-cos-grant-read',
        storage_class='x-cos-storage-class',
        range='Range',
        if_match='If-Match',
        if_none_match='If-None-Match',
        if_modified_since='If-Modified-Since',
        if_unmodified_since='If-Unmodified-Since',
        copy_source_if_match='x-cos-copy-source-If-Match',
        copy_source_if_none_match='x-cos-copy-source-If-None-Match',
        copy_source_if_modified_since='x-cos-copy-source-If-Modified-Since',
        copy_source_if_unmodified_since='x-cos-copy-source-If-Unmodified-Since',
        version_id='x-cos-version-id',
    )
    _region_map = {
        'cn-north': 'cn-north',
        'cn-south': 'cn-south',
        'cn-east': 'cn-east',
        'cn-south-2': 'cn-south-2',
        'cn-southwest': 'cn-southwest',
        'sg': 'sg',
        'cossh': 'cos.ap-shanghai',
        'cosgz': 'cos.ap-guangzhou',
        'cosbj': 'cos.ap-beijing',
        'costj': 'cos.ap-beijing-1',
        'coscd': 'cos.ap-chengdu',
        'cossgp': 'cos.ap-singapore',
        'coshk': 'cos.ap-hongkong',
        'cosca': 'cos.na-toronto',
        'cosger': 'cos.eu-frankfurt',
    }

    def __init__(self, region, access_id, access_key, **kwargs):
        """初始化 Config 类


        :param region(str): 所在节点.
        :param access_id(str): 秘钥secret ID.
        :param access_key(str): 秘钥secret Key.
        :param bucket(str): 存储桶.
        :param appid(str): 用户APPID.
        :param scheme(str): http/https.
        :param token(str): 临时秘钥使用的token.
        :param timeout(int): http超时时间.
        :param retry(int): 失败重试的次数.
        :param session(object): http session(requests module).
        """
        self.access_id = access_id
        self.access_key = access_key
        self.region = self.format_region(region)
        self.appid = kwargs.get('appid', '')
        self.bucket = kwargs.get('bucket', '')
        self.scheme = kwargs.get('scheme', 'https')
        self.auth = AuthFactory(self.access_id, self.access_key)

        logger.info('config parameter-> appid: %s, region: %s', self.appid,
                    self.region)

    def format_region(self, region):
        """格式化地域"""
        if self._region_map.get(region):
            region = self._region_map.get(region)
        elif not region.startswith('cos.'):
            region = 'cos.' + region  # 新域名加上cos.

        return region

    def extract_headers(self, headers):
        """S3到COS参数的一个映射"""
        return {
            self._maplist[header]: headers[header]
            for header in headers if header in self._maplist
        }

    @staticmethod
    def get_md5(data):
        """Render a MD5 String."""
        return base64.standard_b64encode(md5(data).digest())

    @staticmethod
    def dict_to_xml(data, root_node='CompleteMultipartUpload'):
        """V5使用xml格式，将输入的dict转换为xml"""
        xml_dict_obj = XMLParser(data)
        result = xml_dict_obj.to_xml_bytes(root_node)
        return result

    @staticmethod
    def mul_dict_to_xml(data, root_node='CompleteMultipartUpload'):
        """V5使用xml格式，将输入的dict转换为xml"""
        doc = minidom.Document()
        root = doc.createElement(root_node)
        doc.appendChild(root)

        try:
            for i in data['Part']:
                nodePart = doc.createElement('Part')
                nodeNumber = doc.createElement('PartNumber')
                nodeNumber.appendChild(
                    doc.createTextNode(str(i['PartNumber'])))
                nodeETag = doc.createElement('ETag')
                nodeETag.appendChild(doc.createTextNode(str(i['ETag'])))
                nodePart.appendChild(nodeNumber)
                nodePart.appendChild(nodeETag)
                root.appendChild(nodePart)
        except KeyError as exception:
            raise CosClientError(
                'Invalid Parameter, ' + exception.args[0] + ' Is Required!')

        return doc.toxml('utf-8')

    @staticmethod
    def xml_to_dict(data, force_list=None):
        """V5使用xml格式，将response中的xml转换为dict"""
        return XMLParser(data, force_list).to_dict()

    @staticmethod
    def get_id_from_xml(data, name):
        """解析xml中的特定字段"""
        xml_tree = minidom.parseString(data)
        root_node = xml_tree.documentElement
        result = root_node.getElementsByTagName(name)
        # use childNodes to get a list, if has no child get itself
        return result[0].childNodes[0].nodeValue

    @staticmethod
    def format_xml(data, root_node, lst=None):
        """将dict转换为xml"""
        xml_config = dicttoxml(
            data,
            item_func=lambda x: x,
            custom_root=root_node,
            attr_type=False)
        if lst:
            for i in lst:
                xml_config = xml_config.replace(i + i, i)

        return xml_config

    @staticmethod
    def gen_copy_source_range(begin_range, end_range):
        """拼接bytes=begin-end形式的字符串"""
        range_tag = 'bytes={first}-{end}'.format(
            first=begin_range, end=end_range)
        return range_tag


class Client(Config):
    """cos客户端类，封装相应请求"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._token = kwargs.get('token', '')
        self._timeout = kwargs.get('timeout', 30)
        self._retry = kwargs.get('retry', 1)  # 重试的次数，分片上传时可适当增大
        self._session = kwargs.get('session', session())

    def get_url(self, path='', params=None, **kwargs):
        """拼接URL

        :param path(str): 请求COS的路径.
        :param params(str): 请求参数.
        :param bucket(str): 存储桶名称.
        :param appid(str): APPID.
        :param region(str): 存储节点名称.
        :param scheme(str): 请求协议 http/https.
        :return(str): 拼接好的URL.
        """

        result = '{bucket}-{appid}.{region}.myqcloud.com/{path}'.format(
            bucket=kwargs.get('bucket') or self.bucket,
            appid=kwargs.get('appid') or self.appid,
            region=kwargs.get('region') or self.region,
            path=parse.quote(path, '/-_.~').lstrip('/'))
        if not kwargs.get('no_scheme'):
            result = kwargs.get('scheme') or self.scheme + '://' + result
        if params:
            result += '?' + parse.urlencode(params or {})
        return result

    def get_auth(self, method, bucket=None, **kwargs):
        """获取签名

        :param method(str): HTTP Method,如'PUT','GET'.
        :param bucket(str): 存储桶名称.
        :param path(str): 请求COS的路径.
        :param expired(int): 签名有效时间,单位为s.
        :param headers(dict): 签名中的 HTTP Headers.
        :param params(dict): 签名中的 HTTP Params.
        :return (str): 计算出的V5签名.
        """
        url = self.get_url(
            bucket=bucket or self.bucket, path=kwargs.get('path'))

        r = Request(
            method=method,
            url=url,
            headers=kwargs.get('headers'),
            params=kwargs.get('params'))

        auth = self.auth(**kwargs)

        return auth(r).headers['Authorization']

    def send_request(self, method, url, **kwargs):
        """封装request库发起http请求"""
        kwargs['headers']['User-Agent'] = 'cos-python-sdk-v5'
        kwargs['auth'] = self.auth(kwargs.pop('path', '/'))

        if self._token:
            kwargs['headers']['x-cos-security-token'] = self._token

        kwargs['timeout'] = kwargs.pop('timeout', self._timeout)

        try:
            for _ in range(self._retry):
                res = self._session.__getattribute__(method.lower())(url,
                                                                     **kwargs)
                if res.status_code < 300:
                    return res
        except Exception as e:  # 捕获requests抛出的如timeout等客户端错误,转化为客户端错误
            logger.exception('url:%s, exception:%s', url, e)
            raise CosClientError(str(e))

        if res.status_code >= 400:  # 所有的4XX,5XX都认为是COSServiceError
            print(res.headers)
            print(res.status_code)
            print(res.text)
            if method == 'HEAD' and res.status_code == 404:  # Head 需要处理
                msg = dict(
                    code='NoSuchResource',
                    message='The Resource You Head Not Exist',
                    resource=url,
                    requestid=res.headers['x-cos-request-id'],
                    traceid=res.headers['x-cos-trace-id'])
            else:
                msg = res.text or res.headers  # 服务器没有返回Error Body时 给出头部的信息

            logger.error(msg)
            raise CosServiceError(method, msg, res.status_code)

    def _get(self, **kwargs):
        return self.send_request(method='GET', stream=True, **kwargs)

    def _post(self, **kwargs):
        return self.send_request(method='POST', **kwargs)

    def _put(self, **kwargs):
        return self.send_request(method='PUT', **kwargs)

    def _delete(self, **kwargs):
        return self.send_request(method='DELETE', **kwargs)

    def _head(self, **kwargs):
        return self.send_request(method='HEAD', **kwargs)

    def assemble_source(self, path, bucket='', region='', appid='', url=''):
        """拼装资源包"""
        if not url:
            appid = appid or self.appid
            bucket = bucket or self.bucket
            region = self.format_region(region) if region else self.region

            source = dict(appid=appid, bucket=bucket, region=region, path=path)
            source['url'] = self.get_url(no_scheme=True, **source)
        else:
            source = dict(
                appid=appid, bucket=bucket, region=region, path=path, url=url)

        return source
