# -*-coding:utf-8 -*-
"""
:创建时间: 2023/8/14 3:05
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
import requests
import datetime

root_url = 'http://localhost:8000/sgtone'
test_auth_token = 'test'

# test private
res = requests.post(
    root_url + '/private/update_auth_token',
    json={
        'key': 'test_sgtone_key',
        'token': test_auth_token,
        'end_time': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
    }
).json()
print('update_auth_token', res)

# test public
test_list = [
    {
        'url': '/public/check_auth_token',
        'json': {
            'auth_token': test_auth_token,
        },
    },
    {
        'url': '/public/create_sgt_model',
        'json': {
            'name': 'test',
            'client_data': {},
            'in_size': 64,
            'out_size': 4,
            'is_public': True,
        },
    },
    {
        'url': '/public/read_my_sgt_model',
        'json': {},
    },
    {
        'url': '/public/read_public_sgt_model',
        'json': {},
    },
    {
        'url': '/public/clone_sgt_model_to_mine',
        'json': {
            'new_name': 'test2',
            'author_unique_id': 'test',
            'name': 'test',
        },
    },  # the case unable to pass
    {
        'url': '/public/run_sgt_model',
        'json': {
            'name': 'test',
            'data': [[1] * 64, [2] * 64, [3] * 64],
        },
    },
    {
        'url': '/public/upload_sgt_model_train_data',
        'json': {
            'name': 'test',
            'train_data': [[[1] * 64, [1] * 4], [[2] * 64, [2] * 4], [[3] * 64, [3] * 4]],
        },
    },
]
for i in test_list:
    url = root_url + i['url']
    print('test: {}'.format(url))
    res = requests.post(
        url,
        json=i['json'] | {'auth_token': test_auth_token}
    ).json()
    print('result: {}'.format(res))
