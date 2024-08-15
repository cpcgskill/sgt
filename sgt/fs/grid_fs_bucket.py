# -*-coding:utf-8 -*-
"""
:创建时间: 2023/12/31 16:10
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division


from typing import *

from sgt.protocol import FSProtocol

from sgt.db import get_grid_fs_bucket


class GridFS(FSProtocol):
    def save_file(self, file_name: AnyStr, buf: bytes):
        bucket = get_grid_fs_bucket()
        bucket.upload_from_stream(file_name, buf)
    
    
    def read_file(self, file_name: AnyStr) -> bytes:
        bucket = get_grid_fs_bucket()
        with bucket.open_download_stream_by_name(file_name) as stream:
            return stream.read()
    
    
    def update_file(self, file_name: AnyStr, buf: bytes):
        bucket = get_grid_fs_bucket()
    
        old_file_id = [i._id for i in bucket.find({'filename': file_name})]
    
        bucket.upload_from_stream(file_name, buf)
    
        for i in old_file_id:
            bucket.delete(i)
    
    
    def remove_file(self, file_name: AnyStr):
        bucket = get_grid_fs_bucket()
        for file in bucket.find({'filename': file_name}):
            bucket.delete(file._id)
    
    
    def clone_file(self, file_name: AnyStr, new_file_name: AnyStr):
        bucket = get_grid_fs_bucket()
        with bucket.open_download_stream_by_name(file_name) as stream:
            bucket.upload_from_stream(new_file_name, stream)
