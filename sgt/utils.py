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

import io
from typing import *
import datetime
import uuid
import torch

from sgt.protocol import CheckpointProtocol
from sgt.db import with_write_only_collection, with_read_only_collection, get_grid_fs_bucket


def make_device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


def save_checkpoint_to_gridfs(checkpoint: CheckpointProtocol) -> AnyStr:
    """
    保存模型到 gridfs

    :return:
    """
    bucket = get_grid_fs_bucket()
    file_id = f'checkpoint/{uuid.uuid4().hex}'
    checkpoint = checkpoint.to_checkpoint()
    buf = io.BytesIO()
    torch.save(checkpoint, buf)
    buf = buf.getvalue()

    bucket.upload_from_stream(file_id, buf)
    return file_id


def load_checkpoint_from_gridfs(checkpoint_type: Type[CheckpointProtocol], file_id: AnyStr) -> CheckpointProtocol:
    """
    从 gridfs 读取模型
    :return: CheckpointProtocol
    """
    bucket = get_grid_fs_bucket()
    with bucket.open_download_stream_by_name(file_id) as stream:
        # checkpoint = torch.load(io.BytesIO(stream.read()))
        checkpoint = torch.load(stream)
    return checkpoint_type.from_checkpoint(checkpoint)


def remove_checkpoint_from_gridfs(file_id: AnyStr):
    """
    从 gridfs 删除模型
    :param file_id: 模型的 id
    """
    bucket = get_grid_fs_bucket()
    bucket.delete(file_id)


def clone_checkpoint_to_gridfs(checkpoint_file_id: AnyStr) -> AnyStr:
    """
    克隆模型到 gridfs
    :param checkpoint_file_id: 模型的 id
    :return: 新的模型的 id
    """
    bucket = get_grid_fs_bucket()
    with bucket.open_download_stream_by_name(checkpoint_file_id) as stream:
        buf = stream.read()
        new_file_id = f'checkpoint/{uuid.uuid4().hex}'
        bucket.upload_from_stream(new_file_id, stream)
        return new_file_id


__all__ = [
    'make_device',
    'save_checkpoint_to_gridfs',
    'load_checkpoint_from_gridfs',
    'remove_checkpoint_from_gridfs',
    'clone_checkpoint_to_gridfs',
]
