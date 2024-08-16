# Errors

## 目录

- [AuthException](#AuthException)
- [CreateWeightsNetException](#CreateWeightsNetException)
- [FindModelException](#FindModelException)
- [CloneWeightsNetToMineException](#CloneWeightsNetToMineException)
- [RunWeightsNetException](#RunWeightsNetException)
- [UploadDataException](#UploadDataException)

## 错误类型列表

### AuthException

此错误类型表示在进行身份验证时发生的问题

**可能的错误原因**:

1. 请求中缺少`secret_id`或`secret_key`
2. 提供的`secret_id`或`secret_key`不正确
3. `secret_id`已过期
4. 在更新`secret_id`或`secret_key`时，`key`参数与环境变量指定密钥不匹配（如）

### CreateWeightsNetException

此错误类型表示在创建模型时发生的问题

**可能的错误原因**:

1. 模型重命名

### FindModelException

此错误表示找不到模型

**可能的错误原因**:

1. 用户id，模型名称或应用名称错误

### CloneWeightsNetToMineException

此错误类型表示在克隆模型时发生的问题

**可能的错误原因**:

1. 被克隆的模型重命名
2. 被克隆的模型不存在，或提供的模型名称或应用名称错误

### RunWeightsNetException

此错误类型表示在运行模型时发生的问题

**可能的错误原因**:

1. 输入数据的长度不一致
2. 提供的输入数据长度与模型定义的输入大小不匹配

### UploadDataException

此错误类型表示在上传训练数据时发生的问题

**可能的错误原因**:

1. 上传的数据与目标值的长度不一致
2. 上传的数据或目标值的大小与模型定义不一致（例如，输入大小或输出大小与模型不匹配）。