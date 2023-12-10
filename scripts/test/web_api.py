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

import os

if False:
    from typing import *
import requests
import uuid
import datetime
import time
import multiprocessing
import unittest

root_url = 'http://localhost:12000/sgt'
test_key = 'test_sgtone_key'
test_process_num = 8
test_long_run = 100


# test_process_num = os.cpu_count()

class Test(unittest.TestCase):
    def make_secret(self):
        test_secret_id = f'test_{uuid.uuid4().hex}'
        test_secret_key = f'test_{uuid.uuid4().hex}'

        # test private
        res = requests.post(
            root_url + '/private/update_auth_token',
            json={
                'key': test_key,
                'secret_id': test_secret_id,
                'secret_key': test_secret_key,
                'end_time': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            }
        ).json()
        print('update_auth_token', res)

        return test_secret_id, test_secret_key

    def test_make_secret(self):
        print(self.make_secret())

    def test_integrity(self):
        """通过测试所有的接口来测试整体的完整性"""
        test_secret_id, test_secret_key = self.make_secret()

        test_model_name = f'test_{uuid.uuid4().hex}'
        test_input_size = 2048
        test_output_size = 128

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
                    'data': [[1] * test_input_size] * 1024,
                },
            },
            {
                'url': '/public/upload_sgt_model_train_data',
                'json': {
                    'name': test_model_name,
                    'train_data': [[[1] * test_input_size, [1] * test_output_size]] * 1024,
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
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            end_time = time.time()
            print('result: {}'.format(data)[:100])
            print('time: {}'.format(end_time - start_time))

    @staticmethod
    def _run(args):
        url, json = args
        res = requests.post(
            url,
            json=json
        )
        return res.status_code, res.json()

    def test_multi_request(self):
        """测试并发压力测试"""
        secret_id, secret_key = self.make_secret()
        # make a model
        model_name = f'test_{uuid.uuid4().hex}'
        input_size = 64
        output_size = 1

        res = requests.post(
            root_url + '/public/create_sgt_model',
            json={
                'secret_id': secret_id,
                'secret_key': secret_key,
                'app_name': 'test',

                'name': model_name,
                'model_type': 'std',
                'client_data': {},
                'in_size': input_size,
                'out_size': output_size,
                'is_public': True,
            }
        )
        self.assertEqual(res.status_code, 200)
        print('make model')

        # upload data
        res = requests.post(
            root_url + '/public/upload_sgt_model_train_data',
            json={
                'secret_id': secret_id,
                'secret_key': secret_key,
                'app_name': 'test',

                'name': model_name,
                'train_data': [[[1] * input_size, [1] * output_size]] * 1024,
            }
        )
        self.assertEqual(res.status_code, 200)
        print('upload data')

        # run
        args_list = []
        for i in range(100):
            res = (
                root_url + '/public/run_sgt_model',
                {
                    'secret_id': secret_id,
                    'secret_key': secret_key,
                    'app_name': 'test',

                    'name': model_name,
                    'data': [[1] * input_size] * 1024,
                }
            )
            args_list.append(res)

        with multiprocessing.Pool(test_process_num) as p:
            res_list = p.map(Test._run, args_list)
        for status_code, data in res_list:
            print(status_code, data)
        for status_code, _ in res_list:
            self.assertEqual(status_code, 200)

    def test_long_run(self):
        for i in range(test_long_run):
            print(f'long run {i}/{test_long_run}')
            self.test_multi_request()
