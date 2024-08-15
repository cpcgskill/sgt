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

if False:
    from typing import *

import copy
import io
import random
from typing import *

import torch
import torch.nn as nn
from torch import optim


class ASGTModule(object):
    def __init__(self, model_config: List, device: Union[AnyStr, torch.device] = 'cpu'):
        """

        :param model_config: 每一个层的大小 [int, int...]
        """
        super(ASGTModule, self).__init__()

        self.device = device

        self.model_config = model_config

        seq_list = []

        previous_layer_output_size = model_config[0]

        for id_, i in enumerate(model_config):
            seq_list.append(nn.Linear(previous_layer_output_size, i, device=device))
            if id_ >= (len(model_config) - 1):
                seq_list.append(nn.Tanh())
                seq_list.append(nn.Linear(i, i, device=device))
            else:
                seq_list.append(nn.SiLU())
            previous_layer_output_size = i

        self.net = nn.Sequential(*seq_list)
        self.loss_function = nn.MSELoss().to(device)
        self.optimizer = optim.Adagrad(
            self.net.parameters(),
            lr=max(
                1.0 / sum(model_config) + random.gauss(0, 1.0 / sum(model_config) / 2),
                1e-12,
            ),
            weight_decay=max(
                1e-4 + random.gauss(0, 1e-4 / 2),
                1e-12,
            ),
        )

    def initialize_weights(self, std=0.3):
        with torch.no_grad():
            for m in self.net.modules():
                if isinstance(m, nn.Conv2d):
                    torch.nn.init.xavier_normal_(m.weight)
                    if m.bias is not None:
                        torch.nn.init.normal_(m.bias, std=std)
                if isinstance(m, nn.Linear):
                    torch.nn.init.xavier_uniform_(m.weight)
                    if m.bias is not None:
                        torch.nn.init.normal_(m.bias, std=std)
                if isinstance(m, nn.BatchNorm2d):
                    torch.nn.init.xavier_normal_(m.weight)
                    if m.bias is not None:
                        torch.nn.init.normal_(m.bias, std=std)
        return self

    def add_random_value_by_weights(self, std=0.1):
        with torch.no_grad():
            for m in self.net.modules():
                if isinstance(m, nn.Conv2d):
                    m.weight += torch.normal(mean=0, std=std, size=m.weight.size(), device=self.device)
                    if m.bias is not None:
                        m.bias.data += torch.normal(mean=0, std=std, size=m.bias.size(), device=self.device)
                if isinstance(m, nn.Linear):
                    m.weight += torch.normal(mean=0, std=std, size=m.weight.size(), device=self.device)
                    if m.bias is not None:
                        m.bias.data += torch.normal(mean=0, std=std, size=m.bias.size(), device=self.device)
                if isinstance(m, nn.BatchNorm2d):
                    m.weight += torch.normal(mean=0, std=std, size=m.weight.size(), device=self.device)
                    if m.bias is not None:
                        m.bias.data += torch.normal(mean=0, std=std, size=m.bias.size(), device=self.device)
        return self

    def create_checkpoint(self):
        return {
            'model': self.net.state_dict(),
            'model_config': self.model_config,
            'loss_function': self.loss_function.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }

    def create_checkpoint_buffer(self):
        buf = io.BytesIO()
        torch.save(self.create_checkpoint(), buf)
        buf = buf.getvalue()
        return buf

    @staticmethod
    def create_from_checkpoint(checkpoint, device: Union[AnyStr, torch.device] = 'cpu'):
        model = ASGTModule(checkpoint['model_config'], device)
        model.net.load_state_dict(checkpoint['model'])
        model.loss_function.load_state_dict(checkpoint['loss_function'])
        model.optimizer.load_state_dict(checkpoint['optimizer'])
        return model

    def run(self, x):
        with torch.no_grad():
            self.net.eval()
            return self.net(x)

    def train(self, x, y):
        self.net.train()
        self.optimizer.zero_grad()
        output = self.net(x)
        this_loss = self.loss_function(output, y)
        this_loss.backward()
        self.optimizer.step()
        return this_loss


class SGTModule(object):
    def __init__(self, model_list: List, choose_step_size=1024):
        """

        :param model_list: 每一个层的大小 [int, int...]
        :type model_list: List[ASGTModule]
        :type choose_step_size: int
        """
        super(SGTModule, self).__init__()
        self.model_list = model_list
        self.training_count = 0
        self.choose_step_size = choose_step_size
        self.min_loss_list = []
        self.best_model_index = 0

    @staticmethod
    def auto_create(in_size, out_size, model_count=9, choose_step_size=1024):
        this_size = in_size
        model_config = [in_size]
        if in_size > out_size:
            while True:
                this_size = int(this_size / 2)
                if this_size <= out_size:
                    break
                model_config.append(this_size)
        else:
            while True:
                this_size = int(this_size * 2)
                if this_size >= out_size:
                    break
                model_config.append(this_size)
        if out_size > 1:
            for _ in range(3):
                model_config.append(out_size)
        else:
            model_config.append(out_size)
        return SGTModule(
            [ASGTModule(model_config) for _ in range(max(model_count, 1))],
            choose_step_size=choose_step_size,
        ).initialize_weights()

    def initialize_weights(self):
        for i in self.model_list:
            i.initialize_weights(std=0.3)
        return self

    def to_checkpoint(self):
        return {
            'model_list': [i.create_checkpoint() for i in self.model_list],
            'training_count': self.training_count,
            'choose_step_size': self.choose_step_size,
            'min_loss_list': self.min_loss_list,
            'best_model_index': self.best_model_index,
        }

    @staticmethod
    def from_checkpoint(checkpoint, device: Union[AnyStr, torch.device] = 'cpu'):
        model = SGTModule(
            model_list=[ASGTModule.create_from_checkpoint(i, device) for i in checkpoint['model_list']],
            choose_step_size=checkpoint['choose_step_size'],
        )
        model.training_count = checkpoint['training_count']
        model.min_loss_list = checkpoint['min_loss_list']
        model.best_model_index = checkpoint['best_model_index']
        return model

    def run(self, x):
        model = random.choice(self.model_list)
        return model.net(x)

    def train(self, x, y):
        loss_list = [i.train(x, y) for i in self.model_list]
        self.training_count += 1
        with torch.no_grad():
            if not self.training_count < self.choose_step_size:
                self.training_count = 0
                best_loss_index, best_loss = min(
                    enumerate(loss_list),
                    key=lambda i: torch.sum(i[1]),
                )
                self.best_model_index = best_loss_index
                worst_loss_index, worst_loss = max(
                    enumerate(loss_list),
                    key=lambda i: torch.sum(i[1]),
                )
                best_model = self.model_list[best_loss_index]
                best_model_checkpoint = best_model.create_checkpoint()
                new_model = ASGTModule.create_from_checkpoint(best_model_checkpoint, device=best_model.device)
                new_model = new_model.add_random_value_by_weights(torch.max(best_loss))
                if random.random() < 0.5:
                    new_model = new_model.add_random_value_by_weights(0.3)
                self.model_list[worst_loss_index] = new_model
            loss = min([torch.max(i).item() for i in loss_list])
            self.min_loss_list.append(loss)
            return loss

    def is_finish(self):
        """check the checkpoint is finish or not"""
        if len(self.min_loss_list) < 20:
            return False
        # len(self.min_loss_list) = 35, [-5:5] [5:15] [15:25] [25:35]
        chunk_list = [self.min_loss_list[max(len(self.min_loss_list) - i - 10, 0):len(self.min_loss_list) - i] for i in
                      range(0, len(self.min_loss_list), 10)]
        chunk_list = [sum(i) / len(i) for i in chunk_list]
        # 计算梯度
        gradient_list = [chunk_list[i] - chunk_list[i - 1] for i in range(1, len(chunk_list))]
        return abs(gradient_list[-1]) < 0.001
