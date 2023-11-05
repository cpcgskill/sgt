# -*-coding:utf-8 -*-
"""
:创建时间: 2023/10/22 4:03
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import io
import uuid
from typing import *

import torch

from sgt.protocol import CheckpointProtocol
from sgt.db import get_grid_fs_bucket
from sgt.models.std import SGTModule

models = {
    'std': SGTModule,
}


def create_model(model_type: AnyStr, in_size: int, out_size: int) -> CheckpointProtocol:
    """
    创建模型
    :param model_type: 模型类型
    :param in_size: 输入大小
    :param out_size: 输出大小
    :return:
    """
    return models[model_type].auto_create(in_size, out_size)


def save_checkpoint_to_gridfs(checkpoint: CheckpointProtocol) -> AnyStr:
    """
    保存模型到 gridfs

    :return:
    """
    bucket = get_grid_fs_bucket()
    file_name = f'checkpoint/{uuid.uuid4().hex}'
    checkpoint = checkpoint.to_checkpoint()
    buf = io.BytesIO()
    torch.save(checkpoint, buf)
    buf = buf.getvalue()

    bucket.upload_from_stream(file_name, buf)
    return file_name


def load_checkpoint_from_gridfs(model_type: AnyStr, file_name: AnyStr) -> CheckpointProtocol:
    """
    从 gridfs 读取模型
    :return: CheckpointProtocol
    """
    model_type = models[model_type]
    bucket = get_grid_fs_bucket()
    with bucket.open_download_stream_by_name(file_name) as stream:
        checkpoint = torch.load(io.BytesIO(stream.read()))
        # checkpoint = torch.load(stream)
    return model_type.from_checkpoint(checkpoint)


def update_checkpoint_to_gridfs(checkpoint: CheckpointProtocol, file_name: AnyStr) -> AnyStr:
    """
    更新模型到 gridfs

    :return:
    """
    bucket = get_grid_fs_bucket()

    old_file_id = [i._id for i in bucket.find({'filename': file_name})]

    checkpoint = checkpoint.to_checkpoint()
    buf = io.BytesIO()
    torch.save(checkpoint, buf)
    buf = buf.getvalue()

    bucket.upload_from_stream(file_name, buf)

    for i in old_file_id:
        bucket.delete(i)
    return file_name


def remove_checkpoint_from_gridfs(file_name: AnyStr):
    """
    从 gridfs 删除模型
    :param file_name: 模型的 id
    """
    bucket = get_grid_fs_bucket()
    for file in bucket.find({'filename': file_name}):
        bucket.delete(file._id)


def clone_checkpoint_to_gridfs(file_name: AnyStr) -> AnyStr:
    """
    克隆模型到 gridfs
    :param file_name: 模型的 id
    :return: 新的模型的 id
    """
    bucket = get_grid_fs_bucket()
    with bucket.open_download_stream_by_name(file_name) as stream:
        # buf = stream.read()
        new_file_id = f'checkpoint/{uuid.uuid4().hex}'
        bucket.upload_from_stream(new_file_id, stream)
        return new_file_id


def list_model_type():
    return list({'typename': i} for i in models.keys())
