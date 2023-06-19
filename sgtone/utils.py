# -*-coding:utf-8 -*-
"""
:创建时间: 2023/2/14 15:00
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

if False:
    from typing import *
import os
import contextlib
from threading import Lock
from readerwriterlock import rwlock

import pymongo
import torch


def string_to_datetime(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def datetime_to_string(d):
    return d.strftime('%Y-%m-%d %H:%M:%S')


def make_device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


client = pymongo.MongoClient(os.environ['mongodb_database_url'])


def connect_to_database():
    # database = client['sgtone']
    database = client.get_default_database()
    return database


def get_collection(name):
    return connect_to_database().get_collection(name)


_lock_table_lock = Lock()
_rwlock_table = dict()  # type: Dict[AnyStr, rwlock.RWLockFair]


# _rlock_table = dict()  # type: Dict[AnyStr, RLock]


@contextlib.contextmanager
def with_write_only_collection(name):
    """

    :type name: AnyStr
    # :rtype: ContextManager[Collection[Mapping[str, Any]], Any, None]
    """
    with _lock_table_lock:
        if not name in _rwlock_table:
            # _rwlock_table[name] = rwlock.RWLockFair(lock_factory=lambda: RLock())
            _rwlock_table[name] = rwlock.RWLockFair()
        this_lock = _rwlock_table[name]
    with this_lock.gen_wlock():
        yield get_collection(name)


@contextlib.contextmanager
def with_read_only_collection(name):
    """

    :type name: AnyStr
    # :rtype: ContextManager[Collection[Mapping[str, Any]], Any, None]
    """
    with _lock_table_lock:
        if not name in _rwlock_table:
            # _rwlock_table[name] = rwlock.RWLockFair(lock_factory=lambda: RLock())
            _rwlock_table[name] = rwlock.RWLockFair()
        this_lock = _rwlock_table[name]
    with this_lock.gen_rlock():
        yield get_collection(name)


def initialize_database():
    db = connect_to_database()
    collection_names = db.list_collection_names()
    if not 'auth_token' in collection_names:
        collection = db.create_collection('auth_token')
        collection.create_index('end_time')
        collection.create_index('token')
    if not 'checkpoint' in collection_names:
        collection = db.create_collection('checkpoint')
    if not 'data' in collection_names:
        collection = db.create_collection('data')
        collection.create_index('checkpoint_id')
        collection.create_index('user_unique_id')
