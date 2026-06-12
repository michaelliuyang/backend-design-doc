# 错误码设计规则

## 概述
系统采用分层错误码体系，按功能模块与错误类型划分，便于问题定位与设计校验。

---

## 一、客户端错误码（`ClientResponseCode`）

### 41xxx - 认证与授权类错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 0 | 成功 | 200 |
| 41000 | 会话超时，请重新登录 | 403 |
| 41001 | 您没有权限 | 401 |
| 41002 | 您已在另一个设备登录 | 418 |
| 41003 | 资源未找到 | 400 |
| 41004 | 请求大小超出限制 | 413 |
| 41005 | 未获取到 token | 403 |

### 42xxx - 请求参数类错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 42000 | 请求错误 | 400 |
| 42001 | 参数为空 | 400 |
| 42002 | 参数不正确 | 400 |
| 42003 | 不支持的文件类型 | 400 |
| 42004 | 媒体类型错误 | 415 |
| 42005 | 上传文件大小超出限制 | 400 |
| 42006 | 上传文件任务已失败 | 400 |
| 42007 | 您不是本校果之用户，无权限查看 | 400 |
| 42008 | 方法类型不支持 | 405 |
| 42009 | 签名验证错误 | 400 |

### 43xxx - 服务类错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 43000 | 服务已过期 | 400 |

### 44xxx - 用户类错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 44000 | 用户同步错误 | 400 |

### 45xxx - 其他类错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 45000 | 请先同意知识中心协议 | 400 |

---

## 二、服务端错误码（`ServerResponseCode`）

### 50xxx - 服务器内部错误

| 错误码 | 含义 | HTTP 状态码 |
| --- | --- | --- |
| 50000 | 出了点小状况，请稍后重试。 | 500 |
| 50001 | 服务出了点小问题，我们会尽快恢复，请稍后重试。 | 503 |
| 50002 | 网络有点忙，请稍后重试。 | 504 |

---

## 三、Servlet 相关错误码（`ServletResponseCode`）

### 40xxx - Servlet 异常映射

| 错误码 | 异常类名 | 含义 | HTTP 状态码 |
| --- | --- | --- | --- |
| 40000 | MethodArgumentNotValidException | 请求参数验证失败 | 400 |
| 40001 | MethodArgumentTypeMismatchException | 请求参数类型不匹配 | 400 |
| 40002 | MissingServletRequestPartException | 请求 Part 缺失 | 400 |
| 40003 | MissingPathVariableException | 请求 PathVariable 缺失 | 400 |
| 40004 | BindException | 请求绑定错误 | 400 |
| 40005 | MissingServletRequestParameterException | 请求参数缺失 | 400 |
| 40006 | TypeMismatchException | 请求参数类型匹配错误 | 400 |
| 40007 | ServletRequestBindingException | 请求绑定错误 | 400 |
| 40008 | HttpMessageNotReadableException | 请求信息不可读 | 400 |
| 40009 | NoHandlerFoundException | 未找到 | 404 |
| 40010 | NoSuchRequestHandlingMethodException | 未找到此请求 | 404 |
| 40011 | HttpRequestMethodNotSupportedException | 不支持的 HttpMethod 方法 | 405 |

---

## 错误码设计规则总结

### 4. HTTP 状态码映射
- `200`：OK（成功）
- `400`：Bad Request（客户端请求错误）
- `401`：Unauthorized（身份认证失败）
- `403`：Forbidden（权限不足）
- `404`：Not Found（资源不存在）
- `405`：Method Not Allowed（方法不支持）
- `413`：Payload Too Large（请求体过大）
- `415`：Unsupported Media Type（媒体类型不支持）
- `418`：I'm A Teapot（设备重复登录）
- `500`：Internal Server Error（服务器内部错误）
- `503`：Service Unavailable（服务不可用）
- `504`：Gateway Timeout（网关超时）

### 5. 使用建议
- 客户端错误码（4xxxx）用于前端展示与问题诊断。
- 服务端错误码（5xxxx）用于日志记录与监控告警。
- Servlet 错误码（40xxx）由框架自动映射，无需业务代码干预。
