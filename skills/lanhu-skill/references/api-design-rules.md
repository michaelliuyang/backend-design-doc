# API 接口设计规则

本文件定义了「接口设计」(api_designer) 分析模式下生成 API 接口时必须遵守的约定。
AI 在生成接口定义时 **必须逐条检查** 本文件中的每一条规则。

---

## 1. HTTP 方法约束

| 允许的方法 | 用途 | 禁止的方法 |
|-----------|------|-----------|
| `GET` | 查询、列表、详情、导出 | PUT, PATCH, DELETE, HEAD, OPTIONS |
| `POST` | 创建、修改、删除、批量操作、状态变更、大于3个查询参数的请求 | — |

- 只允许 `GET` 和 `POST` 两种方法，不得使用其他 HTTP 方法。
- 判断标准：**读操作 = GET，写操作 = POST**。

---

## 2. 参数传递规则

### GET 请求
- 参数通过 **Query Params** 传递。
- 示例：`GET /orders?userId=123&tenantId=456&status=pending`

### POST 请求
- 参数通过 **Request Body（JSON）** 传递，Content-Type 为 `application/json`。
- 必须定义 **Body 对象名称**（大驼峰，如 `CreateOrderReq`）。
- 必须列出对象内的所有字段及类型。
- 对象命名规范：`{动作}{实体}Req`，如 `CreateOrderReq`、`UpdateUserReq`。

---

## 3. 必传参数

**所有接口**（无论 GET 或 POST）必须包含以下两个参数：

| 参数名 | 类型 | 位置(GET) | 位置(POST) | 说明 |
|--------|------|-----------|-----------|------|
| `userId` | Long | Query Param | Body 字段 | 当前操作用户 ID |
| `tenantId` | Long | Query Param | Body 字段 | 租户 ID |

---

## 4. 字段命名规范

- 接口参数名必须使用 **小驼峰（lowerCamelCase）**。
- 参数名必须来源于 **DDL 中定义的字段名**（将 snake_case 转为 camelCase）。
- 禁止自造字段名。若 DDL 中无对应字段，在「待确认」中标注。
- 实体命名Req 请求实体/Resp 响应实体/Query 查询实体

### 转换示例

| DDL 字段名 | 接口参数名 |
|-----------|-----------|
| `order_no` | `orderNo` |
| `created_at` | `createdAt` |
| `user_name` | `userName` |
| `is_deleted` | `isDeleted` |

---

## 5. 接口 URL 规范

- 路径格式：`/{模块名}/{资源名}`
- 资源名使用 **kebab-case**（小写连字符）。
- 示例：`/order/order-items`、`/user/addresses`

---

## 6. 响应格式

统一响应包装结构（仅说明规范，不需要每个接口重复定义）：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

- 详情接口的 `data` 直接返回对象。
- 分页查询统一返回`IPage<T>`，禁止自定义PageResult等

---

## 7. 接口合并规则（防止接口爆炸）

在 STAGE 4 汇总时必须执行接口合并：

### 合并条件
- 同一实体的 CRUD 操作共用同一组接口前缀。
- 相似的查询条件可通过可选参数合并为一个接口。
- 仅状态不同的列表查询合并为一个接口（通过 `status` 参数区分）。

### 禁止的冗余模式
- ❌ 为每种状态创建独立的列表接口（如 `getPendingOrders`、`getCompletedOrders`）。
- ❌ 为同实体的不同筛选条件创建独立接口。
- ❌ 创建仅包装层不同但底层逻辑相同的接口。

### 拆分条件
- 不同业务领域的操作不得合并。
- 权限模型不同的操作不得合并。
- 读写操作不得合并。

---

## 8. 接口分类标签

每个接口必须标注分类：

| 标签 | 说明 |
|------|------|
| `查询` | 列表查询、条件筛选 |
| `详情` | 单条记录详情 |
| `创建` | 新增记录 |
| `修改` | 更新已有记录 |
| `删除` | 删除/软删除 |
| `状态变更` | 审批、启用/禁用等 |
| `批量操作` | 批量删除、批量导出等 |

---

## 10. 与统一评分表的映射关系

`api_designer` 模式必须复用 `references/rd-review-score-rubric.md` 的统一评分表，不得单独发明另一套评分字段。
在接口设计场景中，以下问题必须直接影响统一评分维度：

| 问题 | 影响维度 |
|------|----------|
| 参数无法映射到 DDL 字段 | `engineering_implementability` / `cross_artifact_consistency` |
| 未遵守 GET/POST 约束 | `rule_and_validation_explicitness` |
| 缺少 `userId` / `tenantId` | `engineering_implementability` |
| 接口粒度不合理、接口爆炸 | `risk_and_dependency_control` |
| 页面行为与接口定义不一致 | `cross_artifact_consistency` |

接口设计输出结束后，必须追加统一评分表，并在 `blocking_questions` 中列出所有因 DDL 缺失、字段对不上、接口粒度不确定而阻塞实现的问题。

