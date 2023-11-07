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
import sgt.fs as fs
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
    """
    checkpoint = checkpoint.to_checkpoint()
    buf = io.BytesIO()
    torch.save(checkpoint, buf)
    buf = buf.getvalue()

    file_name = f'checkpoint/{uuid.uuid4().hex}'

    fs.save_file(file_name, buf)
    return file_name


def load_checkpoint_from_gridfs(model_type: AnyStr, file_name: AnyStr) -> CheckpointProtocol:
    """
    从 gridfs 读取模型
    """
    model_type = models[model_type]
    buf = fs.read_file(file_name)
    checkpoint = torch.load(io.BytesIO(buf))
    return model_type.from_checkpoint(checkpoint)


def update_checkpoint_to_gridfs(checkpoint: CheckpointProtocol, file_name: AnyStr) -> AnyStr:
    """
    更新模型到 gridfs
    """
    checkpoint = checkpoint.to_checkpoint()
    buf = io.BytesIO()
    torch.save(checkpoint, buf)
    buf = buf.getvalue()

    fs.update_file(file_name, buf)
    return file_name


def remove_checkpoint_from_gridfs(file_name: AnyStr):
    """
    从 gridfs 删除模型
    """
    fs.remove_file(file_name)


def clone_checkpoint_to_gridfs(file_name: AnyStr) -> AnyStr:
    """
    克隆模型到 gridfs
    :param file_name: 模型的 id
    :return: 新的模型的 id
    """
    new_file_id = f'checkpoint/{uuid.uuid4().hex}'
    fs.clone_file(file_name, new_file_id)
    return new_file_id

def list_model_type():
    return list({'typename': i} for i in models.keys())
