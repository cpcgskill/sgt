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
import uuid
import datetime
import time

root_url = 'http://localhost:12000/sgt'

test_secret_id = f'test_{uuid.uuid4().hex}'
test_secret_key = f'test_{uuid.uuid4().hex}'

test_model_name = f'test_{uuid.uuid4().hex}'
test_input_size = 2048
test_output_size = 128

# test private
res = requests.post(
    root_url + '/private/update_auth_token',
    json={
        'key': 'test_sgtone_key',
        'secret_id': test_secret_id,
        'secret_key': test_secret_key,
        'end_time': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
    }
).json()
print('update_auth_token', res)

# test public
test_list = [
    {
        'url': '/public/check_auth_token',
        'json': {
            'secret_id': test_secret_id,
            'secret_key': test_secret_key,
        },
    },
    {
        'url': '/public/create_sgt_model',
        'json': {
            'name': test_model_name,
            'app_name': 'test',
            'model_type': 'std',
            'client_data': {},
            'in_size': test_input_size,
            'out_size': test_output_size,
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
            'app_name': 'test',
            'author_unique_id': test_secret_id,
            'name': test_model_name,
        },
    },  # the case unable to pass
    {
        'url': '/public/run_sgt_model',
        'json': {
            'name': test_model_name,
            'app_name': 'test',
            'data': [[1] * test_input_size]*1024,
        },
    },
    {
        'url': '/public/upload_sgt_model_train_data',
        'json': {
            'name': test_model_name,
            'train_data': [[[1] * test_input_size, [1] * test_output_size]]*1024,
        },
    },
]
for i in test_list:
    url = root_url + i['url']
    print('test: {}'.format(url))
    start_time = time.time()
    res = requests.post(
        url,
        json=i['json'] | {
            'secret_id': test_secret_id,
            'secret_key': test_secret_key,
            'app_name': 'test',
        }
    ).json()
    end_time = time.time()
    print('result: {}'.format(res)[:100])
    print('time: {}'.format(end_time - start_time))
