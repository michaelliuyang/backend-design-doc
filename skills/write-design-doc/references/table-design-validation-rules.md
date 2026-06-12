# 表设计校验规则（DDL + 索引）

## 1) 输入门禁
在给出表设计结论前：
- 最终 DDL 必须使用已确认的数据库表前缀。
- 表结构是可选输入；若缺失，则根据 RP 或用户提示推导并起草。

若缺少数据库表前缀：
- 用户要求最终可执行 DDL 时，停止并先请求确认前缀。
- 用户要求草案、方案评审或 AI Coding 输入时，可使用 `{prefix_}` 占位继续，但必须在 `待确认事项` 中标注“表前缀未确认，最终 DDL 不可直接执行”。

若缺少表结构，可继续，但需给出明确假设，且至少输出主表 DDL 草案。

## 2) 主表与关系表约束
- 主表必须保留 `tenant_id`。
- 主表应保留逻辑删除字段（例如 `is_deleted`）。
- `*_r` 关系表不得包含 `tenant_id`。
- `*_r` 关系表不得包含删除状态字段。

## 3) 命名与字段映射约束
API/DDL 映射必须显式且一致：
- API `createdBy/updatedBy` -> DDL `created_by/updated_by`。
- DDL 使用规范化 snake_case 命名。

教育域映射基线：
- `school_id`
- `school_level`（`char(2)`）
- `grade_code`（固定年级场景）
- `graduate_year`
- `learning_area_id`
- `discipline_code`

若使用结构化输出表示 DDL（例如 JSON 字段），每条 DDL 语句仍应以 `string` 类型文本保存。

## 4) 年级建模决策规则
当需求包含年级语义时，必须先确认建模模式：
- 固定年级模型：使用 `grade_code` 标识年级。
- 学年制年级模型：使用 `graduate_year` + `school_level` 作为组合标识。

校验约束：
- 模式未确认前，不得先行确定年级字段。
- 除非明确有兼容性要求，不得在同一场景中将 `grade_code` 与 `graduate_year` + `school_level` 作为并行主标识混用。
- API/DDL 映射必须与选定模式保持一致。

## 5) MySQL 约束与字段默认值约束
- 不得使用 `FOREIGN KEY`。
- 仅允许 `PRIMARY KEY`、`UNIQUE KEY`、`KEY`。
- 若团队规范要求，整型字段长度需显式声明。
- 除明确说明的特殊场景外，所有字段必须显式声明 `NOT NULL` 且提供 `DEFAULT` 值；禁止依赖数据库隐式默认行为。
- 审计时间字段使用固定定义：
  - `create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`
  - `update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`

## 6) 索引设计校验
不得将“最小粒度优先”当作固定规则。
应遵循 MySQL 最左前缀原则和真实查询谓词：
- 等值过滤列优先。
- 范围/排序列靠后。
- 简单表（非 `*_r` 关系表）默认优先单列索引；仅在存在明确且稳定的多列联合查询/排序模式时，才允许设计联合索引。
- `is_deleted` 不得参与任何索引，包括单列索引与联合索引。
- 关系表优先采用场景化索引，不要一味堆叠超大复合索引。

## 7) Schema 覆盖校验输出
必须输出覆盖矩阵：
- 当前 Schema 覆盖情况
- 差距结论

覆盖状态：
- 已覆盖
- 部分覆盖
- 未覆盖

当未提供表结构时，输出还必须包含：
- 推导 DDL 的关键假设。
- 符合本规则集的主表 DDL 草案与索引草案。
- 年级建模决策及字段策略（`grade_code` 或 `graduate_year` + `school_level`）。

所有生成/建议的表名必须一致使用已确认前缀；草案阶段缺少前缀时必须一致使用 `{prefix_}` 占位。
