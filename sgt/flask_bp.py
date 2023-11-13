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

import json
import uuid
from typing import *

import os
import datetime

from bson import ObjectId
from flask import jsonify, request, Blueprint
import torch

import sgt.models as sgt_models

from sgt.db import get_grid_fs_bucket, get_collection
from sgt.fs import save_file, read_file, update_file, remove_file, clone_file

bp = Blueprint('sgt', __name__)


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
    if 'secret_id' not in request.json:
        raise AuthException('secret_id is required')
    secret_id = request.json['secret_id']
    if 'secret_key' not in request.json:
        raise AuthException('secret_key is required')
    secret_key = request.json['secret_key']

    collection = get_collection('secret')
    doc = collection.find_one({'secret_id': secret_id, 'secret_key': secret_key})
    if doc is None:
        raise AuthException('secret is error')
    if 'end_time' in doc:
        if datetime.datetime.now() > doc['end_time']:
            # exception
            raise AuthException('secret has expired')
    # new_auth_token = hmac.new(key.encode('utf-8'), auth_token.encode('utf-8'), hashlib.sha256).hexdigest()
    # return new_auth_token
    return doc['secret_id']


@bp.route('/private/update_auth_token', methods=['POST'])
def update_auth_token_route():
    # 获取输入数据
    if request.json['key'] != key:
        raise AuthException('wrong key')
    #
    secret_id = request.json['secret_id']
    secret_key = request.json['secret_key']
    # 简介, 默认为空
    doc = str(request.json.get('doc', ''))
    # 有效期
    end_time = request.json['end_time']
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    collection = get_collection('secret')
    collection.update_one(
        {
            'secret_id': secret_id,
            'secret_key': secret_key,
        },
        {
            '$set': {
                'doc': doc,
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
    collection = get_collection('checkpoint')
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    app_name = str(request.json['app_name'])
    model_type = str(request.json['model_type'])
    client_data = request.json['client_data']
    in_size = int(request.json['in_size'])
    out_size = int(request.json['out_size'])
    is_public = bool(request.json['is_public'])

    # 检查模型是否存在
    if 0 < collection.count_documents({'user_unique_id': user_unique_id, 'name': name, 'app_name': app_name}):
        raise CreateWeightsNetException('model already exists')

    model = sgt_models.create_model(model_type, in_size, out_size)

    # 保存模型
    checkpoint_file_id = sgt_models.save_checkpoint_to_gridfs(model)

    # set to database
    collection.update_one(
        {
            'user_unique_id': user_unique_id,
            'name': name,
            'app_name': app_name,
        },
        {
            '$set': {
                'client_data': client_data,
                'model_type': model_type,
                'in_size': in_size,
                'out_size': out_size,
                'checkpoint_file_id': checkpoint_file_id,
                'is_public': is_public,
            }
        },

        upsert=True
    )
    # 返回 JSON 结果
    return jsonify(None)


class FindModelException(KnowException): pass


def find_model(user_unique_id, name, app_name):
    collection = get_collection('checkpoint')
    # 检查模型是否存在
    if collection.count_documents({'user_unique_id': user_unique_id, 'name': name, 'app_name': app_name}) < 1:
        raise FindModelException('model does not exist')
    # 查找模型
    doc = collection.find_one({
        'user_unique_id': user_unique_id,
        'name': name,
        'app_name': app_name,
    })
    return doc


@bp.route('/public/delete_sgt_model', methods=['POST'])
def delete_sgt_model_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    app_name = str(request.json['app_name'])

    # 检查模型是否存在
    doc = find_model(user_unique_id, name, app_name)

    collection = get_collection('checkpoint')
    collection.delete_one({'user_unique_id': user_unique_id, 'name': name, 'app_name': app_name})

    sgt_models.remove_checkpoint_from_gridfs(doc['checkpoint_file_id'])
    # 返回 JSON 结果
    return jsonify(None)


@bp.route('/public/update_sgt_model_client_data', methods=['POST'])
def update_sgt_model_client_data_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    app_name = str(request.json['app_name'])
    client_data = request.json['client_data']

    # 检查模型是否存在
    _ = find_model(user_unique_id, name, app_name)

    collection = get_collection('checkpoint')

    collection.update_one(
        {
            'user_unique_id': user_unique_id,
            'name': name,
            'app_name': app_name,
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
    collection = get_collection('checkpoint')
    # 获取输入数据
    user_unique_id = check_auth()
    # 返回 JSON 结果
    return jsonify([
        {
            k: str(i[k]) if isinstance(i[k], ObjectId) else i[k] for k in
            ['user_unique_id', 'name', 'client_data', 'model_type', 'in_size', 'out_size']
        }
        for i in collection.find({'user_unique_id': user_unique_id})
    ])


@bp.route('/public/read_public_sgt_model', methods=['POST'])
def read_public_sgt_model_name_route():
    collection = get_collection('checkpoint')
    # 获取输入数据
    _ = check_auth()
    # 返回 JSON 结果
    return jsonify([
        {
            k: str(i[k]) if isinstance(i[k], ObjectId) else i[k] for k in
            ['user_unique_id', 'name', 'client_data', 'model_type', 'in_size', 'out_size']
        }
        for i in collection.find({'is_public': True})
    ])


class CloneWeightsNetToMineException(KnowException): pass


@bp.route('/public/clone_sgt_model_to_mine', methods=['POST'])
def clone_sgt_model_to_mine_route():
    collection = get_collection('checkpoint')
    # 获取输入数据
    user_unique_id = check_auth()
    new_name = str(request.json['new_name'])
    app_name = str(request.json['app_name'])
    author_unique_id = str(request.json['author_unique_id'])
    name = str(request.json['name'])

    # 检查模型是否存在
    if 0 < collection.count_documents({'user_unique_id': user_unique_id, 'name': new_name, 'app_name': app_name}):
        raise CloneWeightsNetToMineException('model already exists')

    # doc = collection.find_one({'user_unique_id': author_unique_id, 'name': name, 'app_name': app_name})
    doc = find_model(author_unique_id, name, app_name)

    new_checkpoint_file_id = sgt_models.clone_checkpoint_to_gridfs(doc['checkpoint_file_id'])

    collection.update_one(
        {
            'user_unique_id': user_unique_id,
            'name': new_name,
            'app_name': app_name,
        },
        {
            '$set': {
                'client_data': doc['client_data'],
                'model_type': doc['model_type'],
                'in_size': doc['in_size'],
                'out_size': doc['out_size'],
                'checkpoint_file_id': new_checkpoint_file_id,
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
    app_name = str(request.json['app_name'])
    data = request.json['data']

    if len(data) == 0:
        return jsonify({'result': []})
    if len(set((len(d) for d in data))) > 1:
        raise RunWeightsNetException('The length of data is inconsistent')

    doc = find_model(user_unique_id, name, app_name)

    if len(data[0]) != doc['in_size']:
        raise RunWeightsNetException('Data length not equal sgt_model in_size')

    model = sgt_models.load_checkpoint_from_gridfs(doc['model_type'], doc['checkpoint_file_id'])

    out_data = model.run(torch.Tensor(data))
    # 返回 JSON 结果
    return jsonify(out_data.tolist())


class UploadDataException(KnowException): pass


@bp.route('/public/upload_sgt_model_train_data', methods=['POST'])
def upload_sgt_model_train_data_route():
    # 获取输入数据
    user_unique_id = check_auth()
    name = str(request.json['name'])
    app_name = str(request.json['app_name'])
    data = request.json['train_data']

    doc = find_model(user_unique_id, name, app_name)
    if len(data) == 0:
        return jsonify({'result': None})
    if len(set(((len(d), len(l)) for d, l in data))) > 1:
        raise UploadDataException('The length of data and label is inconsistent')
    if (doc['in_size'], doc['out_size']) != (len(data[0][0]), len(data[0][1])):
        raise UploadDataException('The length of data or label is inconsistent with the model definition')

    create_time = datetime.datetime.now()

    data_file_name = f'data/{uuid.uuid4().hex}'
    save_file(data_file_name, json.dumps(data).encode('utf-8'))
    # get_grid_fs_bucket().upload_from_stream(
    #     data_file_name,
    #     json.dumps(data).encode('utf-8'),
    # )

    collection = get_collection('data')
    collection.insert_one(
        {
            'user_unique_id': user_unique_id,
            'checkpoint_id': doc['_id'],
            'create_time': create_time,
            'data_size': len(data),
            'data_file_name': data_file_name,
        }
    )
    # 返回 JSON 结果
    return jsonify(None)


@bp.route('/public/list_model_type', methods=['POST'])
def list_model_type_route():
    return jsonify(sgt_models.list_model_type())
