# sgt

A universal AI runtime and training backend based on deep learning and reinforcement learning.

Its design goal is to be used for various fitting tasks, thus it needs to ensure the trained models possess as high robustness as possible with as few datasets as possible.

* [English](./README.en-us.md)
* [中文](./README.md)

## Contents

- [Quick Start](#Quick Start)
    * [Installation](#Installation)
    * [Install Dependencies](#Install Dependencies)
    * [Set Environment Variables](#Set Environment Variables)
    * [Launch](#Launch)
- [Docker Build](#Docker Build)
- [Copyright Notice](#Copyright Notice)

## Quick Start

### Installation

```commandline
git clone git@github.com:cpcgskill/sgt.git
```

### Install Dependencies

```commandline
pip install -r requirements.txt
```

### Set Environment Variables

Windows

```commandline
set mongodb_database_url "your_mongodb_database_url"
```

Linux

```commandline
export mongodb_database_url "your_mongodb_database_url"
```

MacOS(ps: I'm not familiar with MacOS)

```commandline
export mongodb_database_url "your_mongodb_database_url"
```

### Launch

```commandline
python main.py
```

## Docker Build

Pay attention to the "RUN pip install -r requirements.txt -i https://pypi.douban.com/simple" part in the Dockerfile, as it specifies a CDN within China. If you are not Chinese or are not in China, it may cause problems.

## Copyright Notice

This project has signed an Apache-2.0 license, for details please refer to the LICENSE.