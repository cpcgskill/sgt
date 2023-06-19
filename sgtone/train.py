# -*-coding:utf-8 -*-
"""
:创建时间: 2023/2/14 21:13
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import contextlib
import logging
import os
import time
import random

import cachetools
import torch
from torch.utils.data import DataLoader, TensorDataset

from sgtone.model import SGTModule
from sgtone.utils import make_device, with_read_only_collection, with_write_only_collection

# batch_size = 8192
# save_interval = 8
batch_size = 256
save_interval = 256
success_sleep_seconds = 0.3
default_sleep_seconds = 0.1
fail_sleep_seconds = 0.6
is_cat_do_time = True

device = make_device()

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)


def info(*args):
    logger.info(' '.join(['{}'.format(i) for i in args]))


@contextlib.contextmanager
def timing(work_name):
    if is_cat_do_time:
        start = time.process_time()
        yield
        end = time.process_time()
        info('执行', work_name, '耗时', end - start)
    else:
        yield


@cachetools.cached(cachetools.TTLCache(maxsize=16, ttl=30))
def load_data(checkpoint_id):
    with with_read_only_collection('data') as collection:
        if collection.count_documents({'checkpoint_id': checkpoint_id}) > 0:
            docs = collection.find({'checkpoint_id': checkpoint_id})
            data, label = zip(*((i['data'], i['label']) for i in docs))
            data = torch.Tensor(data)
            label = torch.Tensor(label)
            # 将训练数据的特征和标签组合
            dataset = TensorDataset(data, label)
            return DataLoader(
                dataset,
                batch_size,
                shuffle=True,
                pin_memory=True,
            )
        else:
            return None


def remake_tensor_by_device(d):
    return d.to(device) if d.device != device else d


def remake_tensor_list_by_device(*data_list):
    return (remake_tensor_by_device(d) for d in data_list)


def train_model(checkpoint_id):
    with with_read_only_collection('checkpoint') as collection:
        doc = collection.find_one({'_id': checkpoint_id})
    if doc is None:
        time.sleep(fail_sleep_seconds)
        return

    model = SGTModule.create_from_checkpoint_buffer(doc['checkpoint'])

    data_iter = load_data(checkpoint_id)
    if data_iter is None:
        time.sleep(fail_sleep_seconds)
        return

    with timing('train_model(checkpoint_id={}, batch_size={}, save_interval={})'.format(
            checkpoint_id,
            batch_size,
            save_interval
    )):
        for _ in range(save_interval):
            x, y = remake_tensor_list_by_device(*next(iter(data_iter)))
            if torch.max(model.train(x, y).data) < 0.01:
                break

        with with_write_only_collection('checkpoint') as collection:
            if collection.count_documents({'_id': checkpoint_id}) < 1:
                return
            collection.update_one(
                {
                    '_id': checkpoint_id,
                },
                {
                    '$set': {
                        'checkpoint': model.create_checkpoint_buffer(),
                    }
                },
            )


def train_all_model():
    with with_read_only_collection('checkpoint') as collection:
        checkpoint_count = collection.count_documents({})
    if checkpoint_count <= 0:
        time.sleep(success_sleep_seconds)
        return
    with with_read_only_collection('checkpoint') as collection:
        checkpoint_id_list = [doc['_id'] for doc in collection.find()]

    random.shuffle(checkpoint_id_list)

    for checkpoint_id in checkpoint_id_list:
        train_model(checkpoint_id)


def main():
    while True:
        try:
            train_all_model()
            time.sleep(success_sleep_seconds)
        except Exception as e:
            time.sleep(fail_sleep_seconds)
            logging.error('train_all_model({})'.format(repr(e)))


if __name__ == '__main__':
    main()
