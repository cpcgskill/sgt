# -*-coding:utf-8 -*-
"""
:创建时间: 2023/11/5 20:38
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import datetime
from typing import *
from pymongo.errors import DuplicateKeyError, OperationFailure
from contextlib import contextmanager
import time

from sgt.db import connect_to_database, get_collection


class LockError(Exception): pass


class MongoLock:
    """
    :todo 未测试, TTL还无法正常运行
    """

    def __init__(self, collection_name: str, ttl_time: int = 100):
        if ttl_time < 1:
            raise ValueError('ttl_time must be greater than 0')
        self.collection_name = collection_name

        db = self.db
        if self.collection_name not in db.list_collection_names():
            collection = db.create_collection(self.collection_name)
            collection.create_index('lock_id', unique=True)
            collection.create_index('create_time', expireAfterSeconds=ttl_time)

    @property
    def db(self):
        return connect_to_database()

    @property
    def collection(self):
        return get_collection(self.collection_name)

    @contextmanager
    def acquire_lock(self, lock_id: AnyStr, timeout: int = 10):
        """
        :param timeout: seconds
        :return:
        """
        collection = self.collection

        start = time.time()

        while time.time() - start < timeout:

            if collection.count_documents({'lock_id': lock_id}) > 0:
                # lock exists, try again
                time.sleep(0.1)
                continue

            # try insert a lock
            try:
                result = collection.insert_one({
                    'lock_id': lock_id,
                    'create_time': datetime.datetime.utcnow(),
                })
            except DuplicateKeyError:
                # lock exists, try again
                time.sleep(0.1)
                continue

            try:
                yield
                return
            finally:
                # try to delete the lock
                try:
                    collection.delete_one({'_id': result.inserted_id})
                except OperationFailure:
                    # lock has expired, or has been deleted
                    pass

        raise TimeoutError('Timeout waiting for lock')

    @contextmanager
    def try_acquire_lock(self, lock_id: AnyStr):
        collection = self.collection

        # try insert a lock
        if collection.count_documents({'lock_id': lock_id}) > 0:
            raise LockError('Lock exists')

        # try insert a lock
        try:
            result = collection.insert_one({
                'lock_id': lock_id,
                'create_time': datetime.datetime.utcnow(),
            })
        except DuplicateKeyError:
            raise LockError('Lock exists')

        try:
            yield
            return
        finally:
            # try to delete the lock
            try:
                collection.delete_one({'_id': result.inserted_id})
            except OperationFailure:
                # lock has expired, or has been deleted
                pass


if __name__ == '__main__':
    # 使用示例
    mongo_lock = MongoLock('locks')

    with mongo_lock.acquire_lock('my_lock'):
        print('lock acquired')
        time.sleep(1000)
