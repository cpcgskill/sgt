# sgt

一个以深度学习和强化学习为基础的通用ai运行及训练后端。

它的设计目标是用于各种拟合任务，因此它需要让训练出来的模型拥有尽可能高的鲁棒性的同时需要尽可能少的数据集。

* [English](./README.en-US.md)
* [中文](./README.md)

## 目录

- [快速开始](#快速开始)
    * [安装](#安装)
    * [安装依赖项](#安装依赖项)
    * [设置环境变量](#设置环境变量)
    * [启动](#启动)
- [docker编译](#docker编译)
- [版权说明](#版权说明)

## 快速开始

### 安装

```commandline
git clone git@github.com:cpcgskill/sgt.git
```

### 安装依赖项

```commandline
pip install -r requirements.txt
```

### 设置环境变量

Windows

```commandline
set mongodb_database_url "your_mongodb_database_url"
```

Linux

```commandline
export mongodb_database_url "your_mongodb_database_url"
```

MacOS(ps: 我不熟悉MacOS)

```commandline
export mongodb_database_url "your_mongodb_database_url"
```

### 启动

```commandline
python main.py
```

## docker编译

需要注意Dockerfile文件里的“RUN pip install -r requirements.txt -i https://pypi.douban.com/simple”
部分，因为它指定了一个中国境内的CDN所以如果你不是中国人或者身处非中国地区则它可能导致问题。

## 版权说明

该项目签署了Apache-2.0 授权许可，详情请参阅 LICENSE