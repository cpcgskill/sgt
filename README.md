# sgt

一个以深度学习和强化学习为基础的通用ai运行及训练后端。 它的设计目标是用于各种拟合任务，因此它需要让训练出来的模型拥有尽可能高的鲁棒性的同时需要尽可能少的数据集。

总的来说sgt执行的任务基本上是，用户拥有N组输入，以及对应的正确输出，
sgt在用户创建模型并上传这些输入输出（数据集）之后，会自动训练出一个模型，然后用户可以通过http请求来获取这个模型的对新输入的预测输出。


* [English](./README.en-US.md)
* [中文](./README.md)

## 目录

- [快速开始](#快速开始)
    * [安装](#安装)
    * [安装依赖项](#安装依赖项)
    * [设置环境变量](#设置环境变量)
    * [启动服务](#启动服务)
    * [启动训练](#启动训练)
- [docker编译](#docker编译)
- [docker mongodb数据库示例](#docker-mongodb数据库示例)
- [环境变量](#环境变量)
- [开发文档](#开发文档)
- [版权说明](#版权说明)

## 快速开始

### 介绍

sgt的功能分为2个部分， 一个是服务端， 一个是训练端。

- 服务端： 服务端将会打开一个http server， 用于接受模型以及数据的创建、训练、预测等请求。
- 训练端： 训练端将会独立与服务端， 持续的在后台训练模型。

服务端、训练端可以分别部署在不同的机器上， 并且都是可以横向扩展的。
但是至少需要一个服务端， 一个训练端才能正常工作。

### 安装

```commandline
git clone git@github.com:cpcgskill/sgt.git
```

### 安装依赖项

```commandline
pip install -r requirements.txt --find-links https://download.pytorch.org/whl/torch_stable.html
```

### 设置环境变量

在启动服务之前， 你需要设置以下环境变量

1. [mongodb_database_url](#环境变量)， 这里默认设置为[docker mongodb数据库示例](#docker-mongodb数据库示例)的url
2. [sgt_fs](#环境变量)， 这里默认设置为GridFS，减少配置的复杂度
3. [sgtone_key](#环境变量)

**示例**

Windows

```powershell
set mongodb_database_url "mongodb://myUser:myPassword@localhost:27017/myDatabase?authSource=admin"
set sgt_fs "GridFS"
set sgtone_key "your_key"
```

Linux

```shell
export mongodb_database_url "mongodb://myUser:myPassword@localhost:27017/myDatabase?authSource=admin"
export sgt_fs "GridFS"
export sgtone_key "your_key"
```

MacOS

```shell
export mongodb_database_url "mongodb://myUser:myPassword@localhost:27017/myDatabase?authSource=admin"
export sgt_fs "GridFS"
export sgtone_key "your_key"
```

**示例2**

除了直接设置环境变量，还可以在当前目录创建sgt.env文件， 内容如下：

```dotenv
mongodb_database_url="mongodb://myUser:myPassword@localhost:27017/myDatabase?authSource=admin"
sgt_fs="GridFS"
sgtone_key="your_key"
```

### 启动服务

server.py默认监听**127.0.0.1:6006**，可以通过修改**sgt_host**、**sgt_port**来修改监听地址和端口。

```commandline
python server.py
```

### 启动训练

```commandline
python train.py
```

## docker编译

如果你希望使用docker来部署sgt， 你可以通过以下命令来构建docker镜像：

```powershell
docker build -t <your_image_name> .
```

需要注意Dockerfile文件里的“RUN pip install -r requirements.txt -i https://pypi.douban.com/simple”
部分，因为它指定了一个中国境内的CDN所以如果你不是中国人或者身处非中国地区则它可能导致问题。

## docker mongodb数据库示例

如果你需要一个mongodb数据库， 你可以通过以下docker命令来启动一个mongodb数据库：

```powershell
docker run -d --name my_mongodb_container -e MONGO_INITDB_ROOT_USERNAME=myUser -e MONGO_INITDB_ROOT_PASSWORD=myPassword -e MONGO_INITDB_DATABASE=myDatabase -p 27017:27017 mongo
```

## 环境变量

- sgt_env_file: 你的环境变量文件， 你可以通过这个文件来设置环境变量
- mongodb_database_url: 你的mongodb数据库url, sgt运行时的各类数据都会存储在这个数据库中
- sgtone_key: 用于创建token的key， 你可以随意设置这个key， 它仅会保存在内存中， 但是请不要泄露这个key，它可以让任何人创建token。
- sgt_fs: 文件存储系统配置， 可选项是GridFS或者SampleLocalFS
    * GridFS: 使用mongodb数据库存储文件
    * SampleLocalFS: 使用本地文件系统存储文件, 仅支持Linux系统
- sgt_host: 服务端监听的地址，默认为127.0.0.1
- sgt_port: 服务端监听的端口，默认为6006
- sgtd_device: 训练端使用的设备，默认自动从cuda:0、cpu中选择

## 开发文档

- [Web API](./docs/web_api.md)
- [错误](./docs/error.md)

## 版权说明

该项目签署了Apache-2.0 授权