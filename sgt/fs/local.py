# -*-coding:utf-8 -*-
"""
:创建时间: 2023/12/31 17:09
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

import os
import sys

from sgt.protocol import FSProtocol


class SampleLocalFS(FSProtocol):
    def __init__(self, root: str):
        # linux only, must in linux
        if sys.platform != 'linux':
            raise Exception('only support linux')

        self.root = os.path.abspath(root)
        if not os.path.isdir(self.root):
            os.makedirs(self.root)

    def save_file(self, file_name: AnyStr, buf: bytes):
        return self.update_file(file_name, buf)

    def read_file(self, file_name: AnyStr) -> bytes:
        if not os.path.isfile(self.root + '/' + file_name):
            raise FileNotFoundError(file_name)
        with open(self.root + '/' + file_name, 'rb') as f:
            return f.read()

    def update_file(self, file_name: AnyStr, buf: bytes):
        file_name = self.root + '/' + file_name
        dir_name = os.path.dirname(file_name)
        tmp_file_name = file_name + '.tmp'
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        with open(tmp_file_name, 'wb') as f:
            f.write(buf)
        try:
            if os.path.isfile(file_name):
                os.remove(file_name)
        finally:
            os.rename(tmp_file_name, file_name)

    def remove_file(self, file_name: AnyStr):
        os.remove(self.root + '/' + file_name)

    def clone_file(self, file_name: AnyStr, new_file_name: AnyStr):
        self.update_file(new_file_name, self.read_file(file_name))
