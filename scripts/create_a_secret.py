# -*-coding:utf-8 -*-
"""
:PROJECT_NAME: sgt-develop
:File: create_a_secret.py
:Time: 2024/8/14 22:09
:Author: 张隆鑫
"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import requests
import json

url_root = 'http://127.0.0.1:6006/sgt/'

requests.post(url_root + 'private/update_auth_token', json={
    'key': 'test_sgtone_key',
    'secret_id': 'test',
    'secret_key': 'test',
    'end_time': '2024-08-15 22:09:00',
})
