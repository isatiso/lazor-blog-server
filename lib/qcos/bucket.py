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


class Bucket(Client):
    """s3 object interface begin"""

    def get_presigned_download_url(self, path, **kwargs):
        """生成预签名的下载url

        :param path(str): COS路径.
        :param expire(int): 签名过期时间.
        :param bucket(str): 存储桶名称.
        :return(str): 预先签名的下载URL.
        """
        url = self.get_url(path=path, bucket=kwargs.get('bucket'))
        sign = self.get_auth(
            method='GET',
            bucket=kwargs.get('bucket'),
            path=path,
            expire=kwargs.get('expire', 300))

        return url + parse.urlencode(dict(sign=sign))

    def put_object(self, body, path, bucket=None, headers=None, **kwargs):
        """单文件上传接口，适用于小文件，最大不得超过5GB

        :param body(file|string): 上传的文件内容，类型为文件流或字节流.
        :param path(string): COS路径.
        :param bucket(string): 存储桶名称.
        :kwargs: 设置上传的headers.
        :return(dict): 上传成功返回的结果，包含ETag等信息.
        """
        headers = self.extract_headers(kwargs)
        headers.update(headers.pop('Metadata', {}))

        url = self.get_url(bucket=bucket, path=path)

        logger.info('put object, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, path=path, data=body, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def get_object(self, path, bucket=None, **kwargs):
        """单文件下载接口

        :param path(string): COS路径.
        :param bucket(string): 存储桶名称.
        :param kwargs(dict): 设置下载的headers.
        :return(dict): 下载成功返回的结果,包含Body对应的StreamBody,可以获取文件流或下载文件到本地.
        """
        headers = self.extract_headers(kwargs)
        params = {
            key: headers.pop(key)
            for key in headers.keys() if key.startswith('response')
        }

        url = self.get_url(path=path, bucket=bucket)

        logger.info('get object, url=:%s ,headers=:%s', url, headers)

        res = self._get(url=url, path=path, params=params, headers=headers)

        return dict(
            headers=dict(res.headers), body=res.iter_content(chunk_size=1024))

    def delete_object(self, path, bucket=None, **kwargs):
        """单文件删除接口

        :param Bucket(string): 存储桶名称.
        :param Key(string): COS路径.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)

        url = self.get_url(bucket=bucket, path=path)

        logger.info('delete object, url=:%s ,headers=:%s', url, headers)

        res = self._delete(url=url, path=path, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def delete_objects(self, targets, bucket=None, quiet='false', **kwargs):
        """文件批量删除接口,单次最多支持1000个object

        :param Bucket(string): 存储桶名称.
        :param Delete(list): 需要删除的对象路径列表.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 批量删除的结果.
        """
        root = Element('Delete')
        SubElement(root, 'Quiet').text = quiet
        for item in targets:
            object_el = SubElement(root, 'Object')
            SubElement(object_el, 'Key').text = item

        xml_config = b'<?xml version="1.0" encoding="utf-8" ?>' + tostring(root)

        headers = self.extract_headers(kwargs)
        headers['Content-MD5'] = self.get_md5(xml_config)
        headers['Content-Type'] = 'application/xml'

        url = self.get_url(bucket=bucket) + '?delete'

        logger.info('put bucket replication, url=:%s, headers=:%s', url,
                    headers)

        res = self._post(url=url, data=xml_config, path='/', headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Deleted', 'Error']))

    def head_object(self, path, bucket=None, headers=None, **kwargs):
        """获取文件信息

        :param path(str): COS路径.
        :param bucket(str): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 文件的metadata信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(path=path, bucket=bucket)

        logger.info('head object, url=:%s ,headers=:%s', url, headers)

        res = self._head(url=url, path=path, headers=headers)
        return dict(headers=dict(res.headers), body=res.text)

    def copy_object(self,
                    path,
                    source,
                    bucket=None,
                    copy_mode='Copy',
                    **kwargs):
        """文件拷贝，文件信息修改

        :param key(string): 上传COS路径.
        :param source(dict): 拷贝源,包含appid, bucket, region, key.
        :param copy_mode(string): 拷贝状态,可选值'Copy'|'Replaced'.
        :param bucket(string): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 拷贝成功的结果.
        """

        headers = self.extract_headers(kwargs)
        headers.update(headers.pop('Metadata', {}))
        headers['x-cos-copy-source'] = self.assemble_source(**source)['url']
        if copy_mode not in ('Copy', 'Replaced'):
            raise CosClientError('CopyStatus must be Copy or Replaced')
        headers['x-cos-metadata-directive'] = copy_mode

        url = self.get_url(bucket=bucket, path=path)

        logger.info('copy object, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, path=path, headers=headers)

        return dict(headers=dict(res.headers), body=self.xml_to_dict(res.text))

    def list_objects(self, bucket, **kwargs):
        """获取文件列表

        :param bucket(string): 存储桶名称.
        :param prefix(string): 设置匹配文件的前缀.
        :param delimiter(string): 分隔符.
        :param marker(string): 从 marker 开始列出条目.
        :param max_keys(int): 设置单次返回最大的数量,最大为1000.
        :param encoding_type(string): 设置返回结果编码方式,只能设置为url.
        :param kwargs(dict): 设置请求 headers.
        :return(dict): 文件的相关信息，包括 Etag 等信息.
        """

        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket)

        logger.info('list objects, url=:%s, headers=:%s', url, headers)

        params = {
            'prefix': kwargs.get('prefix', ''),
            'delimiter': kwargs.get('delimiter', ''),
            'marker': kwargs.get('marker', ''),
            'max-keys': kwargs.get('max_keys', 1000),
            'encoding-type': 'url'
        }

        res = self._get(url=url, params=params, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Contents']))

    def create_group(self, path, bucket=None, **kwargs):
        """创建分片上传，适用于大文件上传

        :param Bucket(string): 存储桶名称.
        :param Key(string): COS路径.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 初始化分块上传返回的结果，包含UploadId等信息.
        """
        headers = self.extract_headers(kwargs)
        headers.update(headers.pop('Metadata', {}))

        url = self.get_url(bucket=bucket, path=path) + '?uploads'

        logger.info('create multipart upload, url=:%s ,headers=:%s', url,
                    headers)

        rt = self._post(url=url, path=path, headers=headers)

        return dict(headers=dict(rt.headers), body=self.xml_to_dict(rt.text))

    def upload_part(self, path, body, part, upload_id, bucket=None, **kwargs):
        """上传分片，单个大小不得超过5GB

        :param Bucket(string): 存储桶名称.
        :param Key(string): COS路径.
        :param Body(file|string): 上传分块的内容,可以为文件流或者字节流.
        :param PartNumber(int): 上传分块的编号.
        :param UploadId(string): 分块上传创建的UploadId.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 上传成功返回的结果，包含单个分块ETag等信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket, path=path) + '?' + \
            parse.urlencode(dict(partnumber=part, uploadid=upload_id))

        logger.info('put object, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, path=path, data=body, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def end_group(self, path, upload_id, parts, bucket=None, **kwargs):
        """完成分片上传,除最后一块分块块大小必须大于等于1MB,否则会返回错误.

        :param path(str): COS路径.
        :param upload_id(str): 分块上传创建的upload_id.
        :param parts(dict): 所有分块的信息,包含Etag和PartNumber.
        :param bucket(str): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 上传成功返回的结果，包含整个文件的ETag等信息.
        """

        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket, path=path) + \
            '?' + parse.urlencode(dict(UploadId=upload_id))

        logger.info('complete multipart upload, url=:%s ,headers=:%s', url,
                    headers)

        root = Element('CompleteMultipartUpload')
        for item in parts:
            part = SubElement(root, 'Part')
            SubElement(part, 'PartNumber').text = item['part_number']
            SubElement(part, 'ETag').text = item['etag']

        xml_config = b'<?xml version="1.0" encoding="utf-8" ?>' + tostring(root)

        rt = self._post(
            url=url, path=path, data=xml_config, timeout=1200, headers=headers)

        return dict(headers=dict(rt.headers), body=self.xml_to_dict(rt.text))

    def abort_group(self, path, upload_id, bucket=None, **kwargs):
        """放弃一个已经存在的分片上传任务，删除所有已经存在的分片.

        :param Bucket(string): 存储桶名称.
        :param path(string): COS路径.
        :param UploadId(string): 分块上传创建的UploadId.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket, path=path) + '?' + \
            parse.urlencode(dict(uploadid=upload_id))

        logger.info("abort multipart upload, url=:%s ,headers=:%s", url,
                    headers)

        res = self._delete(url=url, path=path, headers=headers)

        return dict(headers=dict(res.headers), body=res.text)

    def list_parts(self, path, upload_id, **kwargs):
        """列出已上传的分片.

        :param bucket(string): 存储桶名称.
        :param path(string): COS路径.
        :param upload_id(string): 分块上传创建的UploadId.
        :param encoding_type(string): 设置返回结果编码方式,只能设置为url.
        :param max_parts(int): 设置单次返回最大的分块数量,最大为1000.
        :param part_number_marker(int): 设置返回的开始处,从PartNumberMarker下一个分块开始列出.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 分块的相关信息，包括Etag和PartNumber等信息.
        """
        headers = self.extract_headers(kwargs)

        bucket = kwargs.get('bucket')
        params = {
            'uploadid': upload_id,
            'part-number-marker': kwargs.get('part_number_marker', 0),
            'max-parts': kwargs.get('max_parts', 1000),
            'encoding-type': 'url'
        }

        url = self.get_url(bucket=bucket, path=path)

        logger.info('list multipart upload, url=:%s, headers=:%s', url,
                    headers)

        rt = self._get(url=url, path=path, headers=headers, params=params)

        return dict(
            headers=dict(rt.headers), body=self.xml_to_dict(rt.text, ['Part']))

    def get_object_acl(self, path, bucket=None, **kwargs):
        """获取object ACL

        :param path(str): COS路径.
        :param bucket(str): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): Object对应的ACL信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket, path=path) + '?acl'

        logger.info('get object acl, url=:%s, headers=:%s', url, headers)

        res = self._get(url=url, path=path, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Grant']))

    def put_object_acl(self, path, acl, bucket=None, **kwargs):
        """设置object ACL

        :param path(str): COS路径.
        :param acl(dict): 设置object ACL规则,
            可选参数值: default|private|public-read|public-read-write
            其中 default 为跟随 bucket 权限.
        :param bucket(str): 存储桶名称, 默认是当前bucket.
        :param kwargs(dict): 通过headers来设置ACL.
        :return: None.
        """
        kwargs['acl'] = acl
        headers = self.extract_headers(kwargs)

        url = self.get_url(bucket=bucket, path=path) + '?acl'

        logger.info('put object acl, url=:%s, headers=:%s', url, headers)

        res = self._put(url=url, path=path, headers=headers)
        return dict(headers=dict(res.headers), body=res.text)

    def list_objects_versions(self, bucket=None, **kwargs):
        """获取文件列表

        :param prefix(str): 设置匹配文件的前缀.
        :param delimiter(str): 分隔符.
        :param marker(str): 从KeyMarker指定的Key开始列出条目.
        :param version_id_marker(str): 从VersionIdMarker指定的版本开始列出条目.
        :param max_keys(int): 设置单次返回最大的数量,最大为1000.
        :param bucket(str): 存储桶名称.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 文件的相关信息，包括Etag等信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?versions'

        logger.info('list objects versions, url=:%s, headers=:%s', url,
                    headers)

        params = {
            'prefix': kwargs.get('prefix', ''),
            'delimiter': kwargs.get('delimiter', ''),
            'key-marker': kwargs.get('key_marker', ''),
            'version-id-marker': kwargs.get('version_id_marker', ''),
            'max-keys': kwargs.get('max_keys', 1000),
            'encoding-type': 'url'
        }

        res = self._get(url=url, params=params, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Version']))

    def list_multipart_uploads(self, bucket=None, **kwargs):
        """获取Bucket中正在进行的分块上传

        :param Bucket(string): 存储桶名称.
        :param Prefix(string): 设置匹配文件的前缀.
        :param Delimiter(string): 分隔符.
        :param KeyMarker(string): 从KeyMarker指定的Key开始列出条目.
        :param UploadIdMarker(string): 从UploadIdMarker指定的UploadID开始列出条目.
        :param MaxUploads(int): 设置单次返回最大的数量,最大为1000.
        :param EncodingType(string): 设置返回结果编码方式,只能设置为url.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 文件的相关信息，包括Etag等信息.
        """
        headers = self.extract_headers(kwargs)
        url = self.get_url(bucket=bucket) + '?uploads'

        logger.info('get multipart uploads, url=:%s ,headers=:%s', url,
                    headers)

        params = {
            'prefix': kwargs.get('prefix', ''),
            'delimiter': kwargs.get('delimiter', ''),
            'key-marker': kwargs.get('key_marker', ''),
            'upload-id-marker': kwargs.get('upload_id_marker', ''),
            'max-uploads': kwargs.get('max_uploads', 1000),
            'encoding-type': 'url'
        }

        res = self._get(url=url, params=params, headers=headers)

        return dict(
            headers=dict(res.headers),
            body=self.xml_to_dict(res.text, ['Upload']))

    def _upload_part(self, path, local_path, size, part_num, bucket,
                     upload_id):
        """从本地文件中读取分块, 上传单个分块,将结果记录在md5——list中

        :param path(string): 分块上传路径名.
        :param local_path(string): 本地文件路径名.
        :param offset(int): 读取本地文件的分块偏移量.
        :param size(int): 读取本地文件的分块大小.
        :param part_num(int): 上传分块的序号.
        :param bucket(string): 存储桶名称.
        :param upload_id(string): 分块上传的uploadid.
        :param etag_lst(list): 保存上传成功分块的MD5和序号.
        :return: None.
        """
        offset = size * (part_num - 1)
        with open(local_path, 'rb') as fp:
            fp.seek(offset, 0)
            rt = self.upload_part(
                body=fp.read(size),
                path=path,
                part=part_num,
                upload_id=upload_id,
                bucket=bucket)
        return dict(part_number=str(part_num), etag=rt['headers']['ETag'])

    def upload_file(self, path, local_path, **kwargs):
        """小于等于100MB的文件简单上传，大于等于100MB的文件使用分块上传

        :param key(str): 分块上传路径名.
        :param local_path(str): 本地文件路径名.
        :param bucket(str): 存储桶名称.
        :param part_size(int): 分块的大小设置.
        :param max_thread(int): 并发上传的最大线程数.
        :param kwargs(dict): 设置请求headers.
        :return: None.
        """
        size = kwargs.get('size', 10)
        # max_thread = kwargs.get('max_thread', 5)
        bucket = kwargs.get('bucket')
        file_size = os.path.getsize(local_path)

        if file_size > 1024 * 1024 * 1024 * 100:
            raise CosClientError(
                'File is too big, it should be smaller than 100G')

        if file_size <= 1024 * 1024 * 10:
            with open(local_path, 'rb') as fp:
                return self.put_object(
                    bucket=bucket, path=path, body=fp, **kwargs)

        part_size = 1024 * 1024 * size  # 默认按照10MB分块,最大支持100G的文件，超过100G的分块数固定为10000
        parts_num = round(file_size / part_size + 0.5)

        # 创建分块上传
        upload_id = self.create_group(
            bucket=bucket, path=path, **kwargs)['body']['UploadId']

        # 上传分块
        etag_lst = [
            self._upload_part(
                bucket=bucket,
                path=path,
                local_path=local_path,
                size=part_size,
                part_num=i,
                upload_id=upload_id) for i in range(1, parts_num + 1)
        ]

        # 完成分片上传
        try:
            res = self.end_group(
                bucket=bucket, path=path, upload_id=upload_id, parts=etag_lst)
        except (CosClientError, CosServiceError) as e:
            res = self.abort_group(
                bucket=bucket, path=path, upload_id=upload_id)
            raise e
        return dict(headers=dict(res.headers), body=res.text)

    def upload_part_copy(self,
                         path,
                         part,
                         upload_id,
                         source,
                         src_range,
                         bucket=None,
                         **kwargs):
        """拷贝指定文件至分块上传

        :param Bucket(string): 存储桶名称.
        :param Key(string): 上传COS路径.
        :param PartNumber(int): 上传分块的编号.
        :param UploadId(string): 分块上传创建的UploadId.
        :param CopySource(dict): 拷贝源,包含Appid,Bucket,Region,Key.
        :param CopySourceRange(string): 拷贝源的字节范围,bytes=first-last。
        :param kwargs(dict): 设置请求headers.
        :return(dict): 拷贝成功的结果.
        """
        headers = self.extract_headers(kwargs)
        headers['x-cos-copy-source'] = self.assemble_source(**source)['url']
        headers['x-cos-copy-source-range'] = src_range

        url = self.get_url(
            bucket=bucket,
            path=path,
            params=dict(partNumber=part, uploadId=upload_id))

        logger.info('upload part copy, url=:%s ,headers=:%s', url, headers)

        res = self._put(url=url, headers=headers, path=path)

        return dict(headers=dict(res.headers), body=self.xml_to_dict(res.text))

    def _upload_part_copy(self, bucket, path, part, upload_id, source,
                          src_range):
        """拷贝指定文件至分块上传,记录结果到lst中去

        :param bucket(string): 存储桶名称.
        :param key(string): 上传COS路径.
        :param part_number(int): 上传分块的编号.
        :param upload_id(string): 分块上传创建的UploadId.
        :param copy_source(dict): 拷贝源,包含Appid,Bucket,Region,Key.
        :param copy_source_range(string): 拷贝源的字节范围,bytes=first-last。
        :param md5_lst(list): 保存上传成功分块的MD5和序号.
        :return: None.
        """

        res = self.upload_part_copy(
            bucket=bucket,
            path=path,
            part=part,
            upload_id=upload_id,
            source=source,
            src_range=src_range)
        return dict(part_number=part, etag=res['ETag'])

    def copy(self,
             path,
             source,
             copy_mode='Copy',
             part_size=10,
             bucket=None,
             **kwargs):
        """文件拷贝，小于5G的文件调用copy_object，大于等于5G的文件调用分块上传的upload_part_copy

        :param Bucket(string): 存储桶名称.
        :param Key(string): 上传COS路径.
        :param CopySource(dict): 拷贝源,包含Appid,Bucket,Region,Key.
        :param CopyStatus(string): 拷贝状态,可选值'Copy'|'Replaced'.
        :param PartSize(int): 分块的大小设置.
        :param MAXThread(int): 并发上传的最大线程数.
        :param kwargs(dict): 设置请求headers.
        :return(dict): 拷贝成功的结果.
        """
        # 同园区直接走copy_object
        if 'region' not in source or source['region'] == self.region:
            response = self.copy_object(
                path=path,
                source=source,
                bucket=bucket,
                copy_mode=copy_mode,
                **kwargs)
            return response

        # 不同园区查询拷贝源object的content-length
        headers = self.extract_headers(kwargs)
        source = self.assemble_source(**source)
        url = 'https://' + source['url']
        spath = source['path']
        file_size = int(
            self._head(url=url, path=spath,
                       headers=headers).headers['Content-Length'])

        # 如果源文件大小小于5G，则直接调用copy_object接口

        if file_size < self.single_upload_length:
            response = self.copy_object(
                bucket=bucket,
                path=path,
                source=source,
                copy_mode=copy_mode,
                **kwargs)
            return response

        # 如果源文件大小大于等于5G，则先创建分块上传，在调用upload_part
        part_size = 1024 * 1024 * part_size  # 默认按照10MB分块
        parts_num = round(file_size / part_size + 0.5)

        # 创建分块上传
        res = self.create_group(bucket=bucket, path=path)
        upload_id = res['body']['UploadId']

        offset = 0
        etag_lst = []
        for i in range(1, parts_num + 1):
            begin = offset
            end = offset + part_size - 1
            offset += part_size
            etag_lst.append(
                self._upload_part_copy(
                    bucket=bucket,
                    path=path,
                    part=i,
                    upload_id=upload_id,
                    source=source,
                    src_range='bytes=%s-%s' % (begin, end),
                ))

        # 完成分片上传
        try:
            res = self.end_group(
                bucket=bucket, path=path, upload_id=upload_id, parts=etag_lst)
        except Exception as e:
            res = self.abort_group(
                bucket=bucket, path=path, upload_id=upload_id)
            raise e
        return res
