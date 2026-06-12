---
name: lanhu-skill
description: 当用户需要分析蓝湖需求文档、设计稿、切图素材、邀请链接或留言板信息时使用。先判断链接类型，再直接调用本技能自带的 lanhu_cli.py，不依赖额外的 MCP 注册。
---

# 蓝湖 Skill

## 概览
本技能直接封装蓝湖业务脚本，不依赖额外的 MCP 注册。
除页面/设计分析外，内置统一的**研发视角需求评审打分**能力：
- 需求/原型分析、设计稿分析在完成主体分析后，必须基于统一 rubric 输出固定评分表。
- 所有评分结论必须使用同一套字段、等级和决策口径，避免不同流程输出漂移。
职责分层如下：
- `scripts/vendor/lanhu_impl.py`：内置上游 `lanhu-mcp` 的核心实现，已裁掉运行 MCP Server 的入口。
- `scripts/lanhu_cli.py`：本技能自己的 CLI 包装层，负责参数解析、命令分发和 JSON 输出。
- `scripts/bootstrap.py`：标准入口。首次使用时自动创建私有 `.venv`、安装依赖并转调 `lanhu_cli.py`。
- `lanhu-skill`：负责识别场景、执行门禁、决定调用顺序。

## 必要输入
- 蓝湖链接，或足以定位蓝湖项目/文档的描述。
- 用户目标：需求分析、设计稿分析、切图导出、协作者查询、留言板操作。
- 运行环境需具备本技能脚本所需依赖，例如 `httpx`、`beautifulsoup4`；涉及截图或邀请链接解析时还需要 `playwright`。
- 若需要访问蓝湖接口，必须提供有效 `LANHU_COOKIE`。

## 硬性门禁
- 未识别链接类型前，不得直接开始分析。
- PRD/原型文档必须先列页面，再分析页面。
- UI 设计稿必须先列设计稿，再分析具体设计。
- 邀请链接必须先解析成正式蓝湖 URL。
- 若脚本依赖缺失，先提示补齐环境，不得继续臆造结果。

## 何时读取参考资料
- 链接判定、参数要求与工具选择，读取 `references/input-rules.md`。
- CLI 用法、环境变量和依赖要求，读取 `references/startup-and-usage.md`。
- 接口设计（api_designer 模式）的命名规范、方法约束、参数规则，读取 `references/api-design-rules.md`。
- 研发视角统一评分标准、固定字段、等级口径与扣分规则，读取 `references/rd-review-score-rubric.md`。

## 工作流
1. 先判断当前环境是否已经存在外部 `lanhu-mcp` 能力；若存在，则优先使用外部能力，不走本 skill 的本地脚本。
2. 若不存在外部 `lanhu-mcp`，统一通过 `python3 skills/lanhu-skill/scripts/bootstrap.py ...` 执行，不要直接调用 vendor 文件。
3. 通过 `python3 skills/lanhu-skill/scripts/bootstrap.py classify-url --url "<url>"` 确认链接类型。
4. 按场景执行标准入口：
   - PRD/原型：`get-pages` -> `analyze-pages`
   - UI 设计稿：`get-designs` -> `analyze-designs`
   - 切图/素材：`get-designs` -> `get-design-slices`
   - 邀请链接：`resolve-invite`
   - 协作者：`get-members`
   - 留言板：`say-list` / `say-detail` / `say` / `say-edit` / `say-delete`
5. 对返回的 JSON 结果做事实与推断分离。
6. 若场景为需求/原型分析或设计稿分析，主体分析完成后必须基于 `references/rd-review-score-rubric.md` 输出统一评分表。

## 输出要求
- 先说明识别出的蓝湖链接类型与执行路径。
- 若执行了本地脚本，必须说明对应 bootstrap 子命令和关键参数。
- 输出必须区分“已调用工具得到的事实”和“基于事实的推断”。
- 若环境不满足，明确列出缺失项，不得继续臆造结果。
- 需求/原型分析与设计稿分析必须追加统一的研发评审评分表，且评分表必须使用固定字段、固定顺序、固定等级和固定决策口径。
- 评分结论必须引用页面/设计/规则/接口等证据，不得脱离事实主观打分。
