# -*-coding:utf-8 -*-
"""
:创建时间: 2023/10/12 2:43
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
import contextlib
from typing import *
import os
import sgt.config as sgt_config
import pymongo
import gridfs

client = pymongo.MongoClient(sgt_config.mongodb_database_url)


def connect_to_database():
    # database = client['sgtone']
    database = client.get_default_database()
    return database


def get_grid_fs_bucket():
    return gridfs.GridFSBucket(connect_to_database())


def get_grid_fs():
    return gridfs.GridFS(connect_to_database())


def get_collection(name):
    return connect_to_database().get_collection(name)


@contextlib.contextmanager
def start_transaction():
    with client.start_session() as session:
        with session.start_transaction():
            yield session


def initialize_database():
    db = connect_to_database()
    collection_names = db.list_collection_names()
    if not 'secret' in collection_names:
        collection = db.create_collection('secret')
        collection.create_index('end_time')
        collection.create_index('token')
    if not 'checkpoint' in collection_names:
        collection = db.create_collection('checkpoint')
        collection.create_index('user_unique_id')
        collection.create_index('name')
        collection.create_index('app_name')
    if not 'data' in collection_names:
        collection = db.create_collection('data')
        collection.create_index('checkpoint_id')
        collection.create_index('user_unique_id')
    if not 'train_status' in collection_names:
        collection = db.create_collection('train_status')
        collection.create_index('checkpoint_id', unique=True)
        collection.create_index('is_finish')


__all__ = [
    'connect_to_database',
    'get_collection',
    'get_grid_fs_bucket',
    'get_collection',
    'start_transaction',
    'initialize_database',
]
