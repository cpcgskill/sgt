#!/bin/bash

# 检查是否有命令传递给脚本
if [ $# -eq 0 ]; then
    echo "请提供要运行的命令。"
    exit 1
fi

# 使用while循环来不断运行和重启命令
while true; do
    echo "运行命令: $*"
    "$@"
    echo "命令退出了，正在重启..."
done
