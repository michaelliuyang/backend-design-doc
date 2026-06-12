# 输入规则与工具路由

## 1. 链接分类

### 设计稿链接
- 典型特征：包含 `tid`、`pid`，不包含 `docId`
- 用途：设计稿列表、设计稿分析、切图导出

### PRD/原型链接
- 典型特征：包含 `tid`、`pid`、`docId`
- 用途：页面列表、页面分析

### 邀请链接
- 典型特征：`/link/#/invite?sid=...`
- 用途：先解析，再进入正式流程

## 2. 工具选择

### PRD/原型
1. `bootstrap.py get-pages`
2. `bootstrap.py analyze-pages`
3. 输出主体分析结果 + 统一研发评审评分表

### UI 设计稿
1. `bootstrap.py get-designs`
2. `bootstrap.py analyze-designs`
3. 输出主体分析结果 + 统一研发评审评分表

### 切图/素材
1. `bootstrap.py get-designs`
2. `bootstrap.py get-design-slices`

### 邀请链接
1. `bootstrap.py resolve-invite`
2. 根据解析后的 URL 重新路由

### 协作者与留言板
- 协作者：`bootstrap.py get-members`
- 留言列表：`bootstrap.py say-list`
- 留言详情：`bootstrap.py say-detail`
- 发布留言：`bootstrap.py say`
- 编辑留言：`bootstrap.py say-edit`
- 删除留言：`bootstrap.py say-delete`

## 3. 门禁规则
- PRD 场景禁止跳过 `lanhu_get_pages` 直接分析。
- 设计稿场景禁止跳过 `lanhu_get_designs` 直接分析。
- 切图场景必须先拿到精确设计稿名称。
- 邀请链接未解析前，禁止假设其为 PRD 或设计稿。
- 若本地脚本依赖缺失，先补环境，再重新执行 CLI。
