# -*-coding:utf-8 -*-
"""
:创建时间: 2023/1/23 3:14
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
from typing import *

import datetime
import hashlib
import hmac

from bson import ObjectId
from flask import jsonify, request, Blueprint
import torch

from sgtone.model import SGTModule
from sgtone.utils import string_to_datetime, datetime_to_string, connect_to_database, with_write_only_collection, \
    with_read_only_collection, initialize_database

initialize_database()

bp = Blueprint('sgtone', __name__)


class KnowException(Exception): pass


public_exception_type_list = [KnowException]


@bp.errorhandler(Exception)
def try_exception(e: Exception):
    if hasattr(e.__class__, '__module__'):
        exception = "{}.{}".format(e.__class__.__module__, e.__class__.__name__)
    else:
        exception = "unknown.{}".format(e.__class__.__name__)
    for pet in public_exception_type_list:
        if isinstance(e, pet):
            return jsonify({'exception': exception, 'message': "{}".format(e)}), 400
    return jsonify({'exception': exception, 'message': "internal exception"}), 400


class AuthException(KnowException): pass


key = os.getenv('sgtone_key', default='test_sgtone_key')


def check_auth() -> AnyStr:
    """
    :return: 用户的唯一id
    """
    if 'auth_token' not in request.json:
        # exception
        raise AuthException('auth token is required')
    auth_token = request.json['auth_token']
    with with_read_only_collection('auth_token') as collection:
        doc = collection.find_one({'token': auth_token})
        if doc is None:
            raise AuthException('auth token is error')
        if 'end_time' in doc:
            if datetime.datetime.now() > doc['end_time']:
                # exception
                raise AuthException('auth token has expired')
        new_auth_token = hmac.new(key.encode('utf-8'), auth_token.encode('utf-8'), hashlib.sha256).hexdigest()
        return new_auth_token


@bp.route('/private/update_auth_token', methods=['POST'])
def update_auth_token_route():
    # 获取输入数据
    if request.json['key'] != key:
        raise AuthException('wrong key')
    token = request.json['token']
    end_time = string_to_datetime(request.json['end_time'])
    with with_write_only_collection('auth_token') as collection:
        collection.update_one(
            {'token': token},
            {
                '$set': {
                    'end_time': end_time
                }
            },
            upsert=True
        )
        # 返回 JSON 结果
        return jsonify(None)


@bp.route('/public/check_auth_token', methods=['POST'])
def check_auth_token_route():
    try:
        check_auth()
        # 返回 JSON 结果
        return jsonify(True)
    except AuthException:
        # 返回 JSON 结果
        return jsonify(False)


class CreateWeightsNetException(KnowException): pass


@bp.route('/public/create_sgt_model', methods=['POST'])
def create_sgt_model_route():
    with with_write_only_collection('checkpoint') as collection:
        # 获取输入数据
        user_unique_id = check_auth()
        name = str(request.json['name'])
        client_data = request.json['client_data']
        in_size = request.json['in_size']
        out_size = request.json['out_size']
        is_public = bool(request.json['is_public'])

        # 检查模型是否存在
        if 0 < collection.count_documents({'user_unique_id': user_unique_id, 'name': name}):
            raise CreateWeightsNetException('model already exists')

        model = SGTModule.auto_create(in_size, out_size)
        model.initialize_weights()

        collection.update_one(
            {
                'user_unique_id': user_unique_id,
                'name': name,
            },
            {
                '$set': {
                    'client_data': client_data,
                    'in_size': in_size,
                    'out_size': out_size,
                    'checkpoint': model.create_checkpoint_buffer(),
                    'is_public': is_public,
                }
            },

            upsert=True
        )
        # 返回 JSON 结果
        return jsonify(None)


class FindModelException(KnowException): pass


def find_model(user_unique_id, name):
    with with_read_only_collection('checkpoint') as collection:
        # 检查模型是否存在
        if collection.count_documents({'user_unique_id': user_unique_id, 'name': name}) < 1:
            raise FindModelException('model does not exist')
        # 查找模型
        doc = collection.find_one({
            'user_unique_id': user_unique_id,
            'name': name,
        })
        return doc


@bp.route('/public/delete_sgt_model', methods=['POST'])
def delete_sgt_model_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])

    # 检查模型是否存在
    _ = find_model(user_unique_id, name)

    with with_write_only_collection('checkpoint') as collection:
        collection.delete_one({'user_unique_id': user_unique_id, 'name': name})
        # 返回 JSON 结果
        return jsonify(None)


@bp.route('/public/update_sgt_model_client_data', methods=['POST'])
def update_sgt_model_client_data_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    client_data = request.json['client_data']

    # 检查模型是否存在
    _ = find_model(user_unique_id, name)

    with with_write_only_collection('checkpoint') as collection:
        collection.update_one(
            {
                'user_unique_id': user_unique_id,
                'name': name,
            },
            {
                '$set': {
                    'client_data': client_data,
                }
            },

            upsert=True
        )
        # 返回 JSON 结果
        return jsonify(None)


@bp.route('/public/read_my_sgt_model', methods=['POST'])
def read_my_sgt_model_route():
    with with_read_only_collection('checkpoint') as collection:
        # 获取输入数据
        user_unique_id = check_auth()
        # 返回 JSON 结果
        return jsonify([
            {
                k: str(i[k]) if isinstance(i[k], ObjectId) else i[k] for k in
                ['user_unique_id', 'name', 'client_data', 'in_size', 'out_size']
            }
            for i in collection.find({'user_unique_id': user_unique_id})
        ])


@bp.route('/public/read_public_sgt_model', methods=['POST'])
def read_public_sgt_model_name_route():
    with with_read_only_collection('checkpoint') as collection:
        # 获取输入数据
        user_unique_id = check_auth()
        # 返回 JSON 结果
        return jsonify([
            {
                k: str(i[k]) if isinstance(i[k], ObjectId) else i[k] for k in
                ['user_unique_id', 'name', 'client_data', 'in_size', 'out_size']
            }
            for i in collection.find({'is_public': True})
        ])


class CloneWeightsNetToMineException(KnowException): pass


@bp.route('/public/clone_sgt_model_to_mine', methods=['POST'])
def clone_sgt_model_to_mine_route():
    with with_write_only_collection('checkpoint') as collection:
        # 获取输入数据
        user_unique_id = check_auth()
        new_name = str(request.json['new_name'])
        author_unique_id = str(request.json['author_unique_id'])
        name = str(request.json['name'])

        # 检查模型是否存在
        if 0 < collection.count_documents({'user_unique_id': user_unique_id, 'name': new_name}):
            raise CloneWeightsNetToMineException('model already exists')

        doc = collection.find_one({'user_unique_id': author_unique_id, 'name': name})

        collection.update_one(
            {
                'user_unique_id': user_unique_id,
                'name': new_name,
            },
            {
                '$set': {
                    'client_data': doc['client_data'],
                    'in_size': doc['in_size'],
                    'out_size': doc['out_size'],
                    'checkpoint': doc['checkpoint'],
                    'is_public': doc['is_public'],
                }
            },

            upsert=True
        )
        # 返回 JSON 结果
        return jsonify(None)


class RunWeightsNetException(KnowException): pass


@bp.route('/public/run_sgt_model', methods=['POST'])
def run_sgt_model_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    data = request.json['data']

    if len(data) == 0:
        return jsonify({'result': []})
    if len(set((len(d) for d in data))) > 1:
        raise RunWeightsNetException('The length of data is inconsistent')

    doc = find_model(user_unique_id, name)

    if len(data[0]) != doc['in_size']:
        raise RunWeightsNetException('data length not equal sgt_model in_size')

    model = SGTModule.create_from_checkpoint_buffer(doc['checkpoint'])
    out_data = model.run(torch.Tensor(data))
    # 返回 JSON 结果
    return jsonify(out_data.tolist())


class UploadDataException(KnowException): pass


@bp.route('/public/upload_sgt_model_train_data', methods=['POST'])
def upload_sgt_model_train_data_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    data = request.json['train_data']

    doc = find_model(user_unique_id, name)
    if len(data) == 0:
        return jsonify({'result': None})
    if len(set(((len(d), len(l)) for d, l in data))) > 1:
        raise UploadDataException('The length of data and label is inconsistent')
    if (doc['in_size'], doc['out_size']) != (len(data[0][0]), len(data[0][1])):
        raise UploadDataException('The length of data or label is inconsistent with the model definition')

    create_time = datetime.datetime.now()
    with with_write_only_collection('data') as collection:
        collection.insert_many((
            {
                'user_unique_id': user_unique_id,
                'checkpoint_id': doc['_id'],
                'create_time': create_time,
                'data': d,
                'label': l,
            } for d, l in data
        ))
        # 返回 JSON 结果
        return jsonify(None)
