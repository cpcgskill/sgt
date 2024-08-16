# SGT API 文档

SGT API 提供了一套用于管理模型的Web API接口，支持模型的创建、删除、运行、克隆、更新等一系列功能
该API还包含了用户身份验证机制

## 目录

- [认证机制](#认证机制)
- [请求和响应](#请求和响应)
- [全局异常处理](#全局异常处理)
- [示例](#示例)
- [API 列表](#api-列表)
    - [更新认证令牌](#更新认证令牌)
    - [检查认证令牌](#检查认证令牌)
    - [创建模型](#创建模型)
    - [删除模型](#删除模型)
    - [更新模型客户端数据](#更新模型客户端数据)
    - [读取用户的所有模型](#读取用户的所有模型)
    - [读取公开的所有模型](#读取公开的所有模型)
    - [克隆模型](#克隆模型)
    - [运行模型](#运行模型)
    - [上传训练数据](#上传训练数据)
    - [列出模型类型](#列出模型类型)

## 认证机制

- 所有API请求都需要进行身份验证，验证方式为`secret_id`和`secret_key`
- [/private/update_auth_token](#1-更新认证令牌)除外，该API用于更新、创建用户的`secret_id`和`secret_key`

## 请求和响应

- 所有API请求和响应的数据格式均为JSON
- 所有API请求均为POST请求
- 所有API接口统一在`/sgt`路径下， 例如`https://example.com/sgt/private/update_auth_token`

**注意**: 为了保证安全性，请在生产环境中使用HTTPS协议进行通信

## 全局异常处理

- **成功状态码**: 200
- **失败状态码**: 400
- **异常格式**:
  ```json
  {
    "exception": "异常类型",
    "message": "错误消息"
  }
  ```
  若发生已知异常（例如`AuthException`），则返回具体的错误消息；否则返回内部异常的通用错误信息

所有异常类型请参考[错误文档](error.md)

## 示例

如需示例可以参考在`/scripts/test/web_api.py`中的测试代码

## API 列表

### 更新认证令牌

- **URL**: `/private/update_auth_token`
- **功能**: 更新用户的认证令牌

- **请求参数**:
  ```json
  {
    "key": "系统密钥",
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "doc": "简介, 默认为空",
    "end_time": "密钥的有效期, 格式为YYYY-MM-DD HH:MM:SS"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 检查认证令牌

- **URL**: `/public/check_auth_token`
- **功能**: 验证用户的认证令牌

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥"
  }
  ```

- **响应示例**:
    - 成功:
      ```json
      true
      ```
    - 失败:
      ```json
      false
      ```

### 创建模型

- **URL**: `/public/create_sgt_model`
- **功能**: 创建一个新的深度学习模型

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "name": "模型名称",
    "app_name": "应用名称",
    "model_type": "模型类型",
    "client_data": "客户端数据",
    "in_size": "输入大小",
    "out_size": "输出大小",
    "is_public": "是否公开"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 删除模型

- **URL**: `/public/delete_sgt_model`
- **功能**: 删除指定的深度学习模型

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "name": "模型名称",
    "app_name": "应用名称"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 更新模型客户端数据

- **URL**: `/public/update_sgt_model_client_data`
- **功能**: 更新指定模型的客户端数据

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "name": "模型名称",
    "app_name": "应用名称",
    "client_data": "客户端数据"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 读取用户的所有模型

- **URL**: `/public/read_my_sgt_model`
- **功能**: 读取当前用户的所有模型信息

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥"
  }
  ```

- **响应示例**:
  ```json
  [
    {
      "user_unique_id": "用户的唯一ID",
      "name": "模型名称",
      "client_data": "客户端数据",
      "app_name": "应用名称",
      "model_type": "模型类型",
      "in_size": "输入大小",
      "out_size": "输出大小",
      "is_public": "是否公开"
    }
  ]
  ```

### 读取公开的所有模型

- **URL**: `/public/read_public_sgt_model`
- **功能**: 读取所有公开的模型信息

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥"
  }
  ```

- **响应示例**:
  ```json
  [
    {
      "user_unique_id": "用户的唯一ID",
      "name": "模型名称",
      "client_data": "客户端数据",
      "app_name": "应用名称",
      "model_type": "模型类型",
      "in_size": "输入大小",
      "out_size": "输出大小",
      "is_public": "是否公开"
    }
  ]
  ```

### 克隆模型

- **URL**: `/public/clone_sgt_model_to_mine`
- **功能**: 将其他用户的模型克隆到自己的账户下

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "new_name": "新的模型名称",
    "app_name": "应用名称",
    "author_unique_id": "模型作者的唯一ID",
    "name": "被克隆模型的名称"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 运行模型

- **URL**: `/public/run_sgt_model`
- **功能**: 运行指定的模型并返回结果

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "name": "模型名称",
    "app_name": "应用名称",
    "data": "输入数据，二维数组形式"
  }
  ```

- **响应示例**:
  ```json
  [
    [输出数据]
  ]
  ```

### 上传训练数据

- **URL**: `/public/upload_sgt_model_train_data`
- **功能**: 上传指定模型的训练数据

- **请求参数**:
  ```json
  {
    "secret_id": "用户的唯一ID",
    "secret_key": "用户的密钥",
    "name": "模型名称",
    "app_name": "应用名称",
    "train_data": "训练数据，二维数组形式，每个元素包含输入和标签"
  }
  ```

- **响应示例**:
  ```json
  null
  ```

### 列出模型类型

- **URL**: `/public/list_model_type`
- **功能**: 列出支持的模型类型

- **请求参数**: 无

- **响应示例**:
  ```json
  [
    "模型类型1",
    "模型类型2",
    ...
  ]
  ```