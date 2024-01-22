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

import traceback

import contextlib
import json
import logging
import time
import random

import cachetools
import torch
from torch.utils.data import DataLoader, TensorDataset

import sgt.models as sgt_models
from sgt.db import get_grid_fs_bucket, get_collection
from sgt.config import fs
from sgt.lock import MongoLock, MongoLockException

train_step = 64 * 4 * 8
batch_size = 64 * 4
save_interval = 64 * 4
success_sleep_seconds = 0.1
default_sleep_seconds = 0.05
fail_sleep_seconds = 0.3
is_cat_do_time = True

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# device = torch.device('cpu')

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)

train_lock = MongoLock('train_lock')


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
def load_data(checkpoint_id, batch_size_):
    collection = get_collection('data')
    if collection.count_documents({'checkpoint_id': checkpoint_id}) > 0:
        docs = collection.find({'checkpoint_id': checkpoint_id})
        data_list = []
        label_list = []
        for i in docs:
            # with fs_bucket.open_download_stream_by_name(i['data_file_name']) as stream:
            #     data_and_label = json.loads(stream.read())
            data_and_label = json.loads(fs.read_file(i['data_file_name']))
            data, label = zip(*data_and_label)
            data = torch.Tensor(data)
            label = torch.Tensor(label)
            data_list.append(data)
            label_list.append(label)
        data = torch.cat(data_list)
        label = torch.cat(label_list)
        # 将训练数据的特征和标签组合
        dataset = TensorDataset(data, label)
        return DataLoader(
            dataset,
            batch_size_,
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
    collection = get_collection('checkpoint')
    status_collection = get_collection('train_status')

    doc = collection.find_one({'_id': checkpoint_id})
    if doc is None:
        time.sleep(fail_sleep_seconds)
        return

    # if the model is finish, then return
    if status_collection.count_documents({'checkpoint_id': checkpoint_id, 'is_finish': True}) > 0:
        if random.random() < 0.5:
            return

    model = sgt_models.load_checkpoint(
        doc['model_type'],
        doc['checkpoint_file_id'],
        device=device,
    )
    if random.random() < 0.3:
        data_iter = load_data(checkpoint_id, random.randint(1, batch_size))
    else:
        data_iter = load_data(checkpoint_id, batch_size)
    if data_iter is None:
        time.sleep(fail_sleep_seconds)
        return

    with timing('train_model(checkpoint_id={}, batch_size={}, save_interval={})'.format(
            checkpoint_id,
            batch_size,
            save_interval
    )):
        for train_idx in range(1, train_step + 1):
            x, y = remake_tensor_list_by_device(*next(iter(data_iter)))
            model.train(x, y)
            # if the train_idx is save_interval, then save model
            if train_idx % save_interval == 0 or train_idx == train_step:
                if model.is_finish():
                    # set model is finish, by update or insert
                    status_collection.update_one(
                        {'checkpoint_id': checkpoint_id},
                        {'$set': {'is_finish': True}},
                        upsert=True,
                    )

                if collection.count_documents({'_id': checkpoint_id}) < 1:
                    return
                sgt_models.update_checkpoint(model, doc['checkpoint_file_id'])


def train_all_model():
    collection = get_collection('checkpoint')
    checkpoint_count = collection.count_documents({})
    if checkpoint_count <= 0:
        time.sleep(success_sleep_seconds)
        return

    checkpoint_id_list = [doc['_id'] for doc in collection.find()]

    random.shuffle(checkpoint_id_list)

    for checkpoint_id in checkpoint_id_list:
        try:
            with train_lock.try_acquire_lock(checkpoint_id):
                train_model(checkpoint_id)
        except MongoLockException:
            pass


def main():
    while True:
        try:
            train_all_model()
            time.sleep(success_sleep_seconds)
        except Exception as e:
            time.sleep(fail_sleep_seconds)
            logging.error('train_all_model error: \n{}'.format(traceback.format_exc()))


def test():
    while True:
        train_all_model()


if __name__ == '__main__':
    test()
