# coding=utf-8
"""COS Bucket Module."""

import logging
import os
from urllib import parse
from xml.etree.ElementTree import Element, SubElement, tostring

from .client import Client
from .exception import CosClientError, CosServiceError

logging.basicConfig(
    level=logging.INFO,
    format=
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='cos_v5.log',
    filemode='a')

logger = logging.getLogger(__name__)


class Region(Client):
    """s3 bucket interface begin"""

    # service interface begin
    def list_buckets(self, **kwargs):
        """列出所有bucket

        :return(dict): 账号下bucket相关信息.
        """
        headers = self.extract_headers(kwargs)

        url = 'http://service.cos.myqcloud.com/'

        res = self._get(url=url, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Bucket']))

    def create_bucket(self, bucket, **kwargs):
        """创建一个bucket

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket)

        logger.info('create bucket, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def delete_bucket(self, bucket, **kwargs):
        """删除一个bucket，bucket必须为空

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket)

        logger.info('delete bucket, url=:%s, headers=:%s', url, headers)

        res = self._delete(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def head_bucket(self, bucket, **kwargs):
        """确认bucket是否存在

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket)

        logger.info('head bucket, url=:%s, headers=:%s', url, headers)

        res = self._head(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def get_bucket_acl(self, bucket, **kwargs):
        """获取bucket ACL

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置headers.
        :return(dict): Bucket对应的ACL信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?acl'

        logger.info('get bucket acl, url=:%s, headers=:%s', url, headers)

        res = self._get(url=url, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Grant']))

    def put_bucket_acl(self, bucket, acl=None, **kwargs):
        """设置bucket ACL

        :param Bucket(string): 存储桶名称.
        :param AccessControlPolicy(dict): 设置bucket ACL规则.
        :param kwargs(dict): 通过headers来设置ACL.
        :return: None.
        """

        kwargs['acl'] = acl
        headers = self.extract_headers(kwargs)

        url = self.get_url(bucket=bucket) + '?acl'

        logger.info('put bucket acl, url=:%s, headers=:%s', url, headers)

        res = self._put(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def get_bucket_cors(self, bucket, **kwargs):
        """获取bucket CORS

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 获取Bucket对应的跨域配置.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?cors'

        logger.info('get bucket cors, url=:%s, headers=:%s', url, headers)

        res = self._get(url=url, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, [
                'CORSRule', 'AllowedOrigin', 'AllowedMethod', 'AllowedHeader',
                'ExposeHeader'
            ]))

    def put_bucket_cors(self, bucket, config='', **kwargs):
        """设置bucket CORS

        :param Bucket(string): 存储桶名称.
        :param CORSConfiguration(list): 设置Bucket跨域规则.
            配置中每一个元素是一个包含构建CORS规则的信息包(dict):
                :param origin: 允许的请求来源, 格式为 <scheme>://<host>[:<port>]
                               如 http://www.qq.com
                :param method: 允许的方法, GET|PUT|HEAD|POST|DELETE
                :param request_header: 允许的请求头部
                :param response_header: 允许的响应头部
                :param max_age_seconds： OPTIONS 请求得到结果的有效期
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """

        root = Element('CORSConfiguration')
        for item in config:
            rule = SubElement(root, 'CORSRule')
            SubElement(rule, 'AllowedOrigin').text = item['origin']
            SubElement(rule, 'AllowedMethod').text = item['method']
            if 'request_header' in item:
                SubElement(rule, 'AllowedHeader').text = item.get(
                    'request_header', ' ')
            if 'response_header' in item:
                SubElement(rule, 'ExposeHeader').text = item.get(
                    'response_header', ' ')
            if 'max_age_seconds' in item:
                SubElement(rule, 'MaxAgeSeconds').text = item.get(
                    'max_age_seconds', ' ')

        xml_config = b'<?xml version="1.0" encoding="utf-8" ?>' + tostring(root)

        headers = self.extract_headers(kwargs)
        headers['Content-MD5'] = self.get_md5(xml_config)
        headers['Content-Type'] = 'application/xml'

        url = self.get_url(bucket=bucket) + '?cors'

        logger.info('put bucket cors, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, data=xml_config, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def delete_bucket_cors(self, bucket, **kwargs):
        """删除bucket CORS

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)

        url = self.get_url(bucket=bucket) + '?cors'

        logger.info('delete bucket cors, url=:%s ,headers=:%s', url, headers)

        res = self._delete(url=url, headers=headers)
        return dict(headers=dict(res.headers), body=res.text)

    def put_bucket_lifecycle(self, bucket, config='', **kwargs):
        """设置bucket LifeCycle

        :param Bucket(string): 存储桶名称.
        :param config(list): 设置Bucket的生命周期规则.
                :param filter: Filter 用于描述规则影响的 Object 集合
                :param status: 指明规则是否启用, 枚举值：Enabled|Disabled
                :param rule_id: 允许的请求头部
                :param response_header: 允许的响应头部
                :param max_age_seconds： OPTIONS 请求得到结果的有效期
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        # lst = ['<Rule>', '<Tag>', '</Tag>', '</Rule>']  # 类型为list的标签
        # xml_config = utils.format_xml(
        #     data=lifecycle_configuration or {},
        #     root_node='LifecycleConfiguration',
        #     lst=lst)

        root = Element('LifecycleConfiguration')
        for item in config:
            rule = SubElement(root, 'Rule')
            SubElement(rule, 'Filter').text = item['origin']
            SubElement(rule, 'Status').text = item['method']
            if 'request_header' in item:
                SubElement(rule, 'AllowedHeader').text = item.get(
                    'request_header', ' ')
            if 'response_header' in item:
                SubElement(rule, 'ExposeHeader').text = item.get(
                    'response_header', ' ')
            if 'max_age_seconds' in item:
                SubElement(rule, 'MaxAgeSeconds').text = item.get(
                    'max_age_seconds', ' ')

        xml_config = b'<?xml version="1.0" encoding="utf-8" ?>' + tostring(root)

        headers = self.extract_headers(kwargs)

        headers['Content-MD5'] = self.get_md5(xml_config)
        headers['Content-Type'] = 'application/xml'

        url = self.get_url(bucket=bucket) + '?lifecycle'

        logger.info('put bucket lifecycle, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, data=xml_config, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def get_bucket_lifecycle(self, bucket, **kwargs):
        """获取bucket LifeCycle

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): Bucket对应的生命周期配置.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?lifecycle'

        logger.info('get bucket cors, url=:%s ,headers=:%s', url, headers)

        res = self._get(url=url, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Rule']))

    def delete_bucket_lifecycle(self, bucket, **kwargs):
        """删除bucket LifeCycle

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?lifecycle'

        logger.info('delete bucket cors, url=:%s, headers=:%s', url, headers)

        res = self._delete(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def put_bucket_versioning(self, bucket, status, **kwargs):
        """设置bucket版本控制

        :param Bucket(string): 存储桶名称.
        :param Status(string): 设置Bucket版本控制的状态，可选值为'Enabled'|'Suspended'.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?versioning'

        logger.info('put bucket versioning, url=:%s ,headers=:%s', url,
                    headers)

        if status not in ('Enabled', 'Suspended'):
            raise CosClientError(
                'versioning status must be set to Enabled or Suspended!')

        xml_config = self.format_xml(
            data=dict(Status=status), root_node='VersioningConfiguration')

        res = self._put(url=url, data=xml_config, headers=headers)
        return dict(headers=dict(res.headers), body=res.text)

    def get_bucket_versioning(self, bucket=None, **kwargs):
        """查询bucket版本控制

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 获取Bucket版本控制的配置.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?versioning'

        logger.info('get bucket versioning, url=:%s ,headers=:%s', url,
                    headers)

        res = self._get(url=url, headers=headers)

        return dict(headers=dict(res.headers), body=self.xml_to_dict(res.text))

    def get_bucket_location(self, bucket=None, **kwargs):
        """查询bucket所属地域

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 存储桶的地域信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?location'

        logger.info('get bucket location, url=:%s ,headers=:%s', url, headers)

        res = self._get(url=url, headers=headers)
        return dict(headers=dict(res.headers), body=self.xml_to_dict(res.text))

    def put_bucket_replication(self,
                               bucket,
                               replication_configuration=None,
                               **kwargs):
        """设置bucket跨区域复制配置

        :param Bucket(string): 存储桶名称.
        :param ReplicationConfiguration(dict): 设置Bucket的跨区域复制规则.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        lst = ['<Rule>', '</Rule>']  # 类型为list的标签
        xml_config = self.format_xml(
            data=replication_configuration or {},
            root_node='ReplicationConfiguration',
            lst=lst)

        headers = self.extract_headers(kwargs)
        headers['Content-MD5'] = self.get_md5(xml_config)
        headers['Content-Type'] = 'application/xml'

        url = self.get_url(bucket=bucket) + '?replication'

        logger.info('put bucket replication, url=:%s, headers=:%s', url,
                    headers)

        res = self._put(url=url, data=xml_config, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def get_bucket_replication(self, bucket, **kwargs):
        """获取bucket 跨区域复制配置

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): Bucket对应的跨区域复制配置.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?replication'

        logger.info('get bucket replication, url=:%s ,headers=:%s', url,
                    headers)

        res = self._get(url=url, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Rule']))

    def delete_bucket_replication(self, bucket, **kwargs):
        """删除bucket 跨区域复制配置

        :param Bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?replication'

        logger.info('delete bucket replication, url=:%s ,headers=:%s', url,
                    headers)

        res = self._delete(url=url, headers=headers)
        return dict(headers=dict(res.headers), body=res.text)
