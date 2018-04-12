import os
from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client

# Django 默认保存文件时，会调用storage类中的save方法
# storage类中的save方法会调用Default_files_storage配置指定的类
# _save方法的返回值最终会保存在表image字段中
# Django保存文件之前，会调用Default_file_storage配置香置顶累
# 中的exist方法
# 判断文件是否存在 防止被覆盖

class FDFSStorage(Storage):
    """fast dfs文件存储"""
    def __init__(self,client_conf=None,nginx_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF

        self.client_conf = client_conf

        if nginx_url is None:
            nginx_url = settings.FDFS_NGINX_URL

        self.nginx_url = nginx_url

    def _save(self,name,content):

        """保存文件调用"""
        client = Fdfs_client(self.client_conf)

        # 获取上传文件
        file_content = content.read()

        # 上传文件
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id, # 保存的文件id
        #     'Status': 'Upload successed.', # 上传是否成功
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # } if success else None

        # 上传文件
        response = client.upload_by_buffer(file_content)

        if response is None or response.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件失败')

        # 成功则保存文件id
        file_id = response.get('Remote file_id')

        # 返回file_id
        return file_id

    def exist(self,name):
        """判断文件是否存在"""
        return False

    def url(self,name):
        """返回可以访问到文件的url地址"""
        # return 'http:/192.168.8.134:8888/' + name
        return self.nginx_url + name