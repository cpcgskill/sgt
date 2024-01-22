# -*-coding:utf-8 -*-
"""
:创建时间: 2023/10/9 3:42
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

from typing import *

import torch


class CheckpointProtocol(Protocol):
    @staticmethod
    def auto_create(in_size: int, out_size: int) -> 'CheckpointProtocol': ...

    def to_checkpoint(self) -> Dict: ...

    @staticmethod
    def from_checkpoint(checkpoint: Dict,  device: Union[AnyStr, torch.device]='cpu') -> 'CheckpointProtocol': ...

    def run(self, x: torch.Tensor) -> torch.Tensor:
        """

        :param x: Shape: [batch, in_size]
        :return: Shape: [batch, out_size]
        """
        ...

    def train(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """

        :param x: Shape: [batch, in_size]
        :param y: Shape: [batch, out_size]
        :return: loss
        """
        ...

    def is_finish(self) -> bool:
        """check the checkpoint is finish or not"""
        ...

class FSProtocol(Protocol):
    def save_file(self, file_name: AnyStr, buf: bytes) -> 'FSProtocol':
        pass

    def read_file(self, file_name: AnyStr) -> bytes:
        pass

    def update_file(self, file_name: AnyStr, buf: bytes) -> 'FSProtocol':
        pass

    def remove_file(self, file_name: AnyStr) -> 'FSProtocol':
        pass

    def clone_file(self, file_name: AnyStr, new_file_name: AnyStr) -> 'FSProtocol':
        pass
