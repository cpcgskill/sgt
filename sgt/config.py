# -*-coding:utf-8 -*-
"""
:创建时间: 2023/12/31 19:07
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import os
import sys

from sgt.protocol import FSProtocol


sgt_fs = os.environ.get('sgt_fs', default='SampleLocalFS')
if sgt_fs == 'SampleLocalFS':
    from sgt.fs.local import SampleLocalFS
    local_path = os.environ.get('local_path', default='~/sgt_fs')
    fs = SampleLocalFS(local_path) # type: FSProtocol
elif sgt_fs == 'GridFS':
    from sgt.fs.grid_fs_bucket import GridFS
    fs = GridFS() # type: FSProtocol
else:
    raise Exception('sgt_fs is not valid')