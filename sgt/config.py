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
import logging

from sgt.protocol import FSProtocol

if os.path.isfile('./sgt.env'):
    import dotenv

    dotenv.load_dotenv('./sgt.env')
if 'sgt_env_file' in os.environ:
    sgt_env_file = os.environ['sgt_env_file']
    if not os.path.isfile(sgt_env_file):
        raise FileNotFoundError(sgt_env_file)
    import dotenv

    dotenv.load_dotenv(sgt_env_file)

if 'mongodb_database_url' not in os.environ:
    raise KeyError("environment variable mongodb_database_url not found, it's required")
mongodb_database_url = os.environ['mongodb_database_url']

key = os.getenv('sgtone_key', default='test_sgtone_key')

is_debug = os.environ.get('sgt_debug', default='false').lower() in {'true', 'on'}

if is_debug:
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    )

host = os.environ.get('sgt_host', '0.0.0.0')
port = int(os.environ.get('sgt_port', '6006'))

_sgt_fs = os.environ.get('sgt_fs', default='SampleLocalFS')
if _sgt_fs == 'SampleLocalFS':
    from sgt.fs.local import SampleLocalFS

    local_path = os.environ.get('local_path', default='~/sgt_fs')
    fs = SampleLocalFS(local_path)  # type: FSProtocol
elif _sgt_fs == 'GridFS':
    from sgt.fs.grid_fs_bucket import GridFS

    fs = GridFS()  # type: FSProtocol
else:
    raise Exception('sgt_fs is not valid')

device = os.environ.get('sgt_device', default=None)
