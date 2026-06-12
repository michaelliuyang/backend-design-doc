# CLI 使用说明

## 1. 设计原则
- 若当前环境已存在外部 `lanhu-mcp`，优先使用外部能力，不再走本地 bootstrap。
- 技能不会自动注册 MCP Server。
- 所有能力统一通过 `scripts/bootstrap.py` 进入。
- `bootstrap.py` 负责首次自动安装依赖，然后再调用 `scripts/lanhu_cli.py`。
- `lanhu_cli.py` 负责分发命令并输出 JSON。

## 2. 运行前置
- 需要本机具备 Python 3。
- 基础依赖：`httpx`、`beautifulsoup4`
- 视觉相关命令额外依赖：`playwright`
- 访问蓝湖接口必须配置 `LANHU_COOKIE`
- 若系统 PATH 中已有 `lanhu-mcp`，或设置了 `LANHU_MCP_COMMAND`，`bootstrap.py` 会短路并提示改走外部 `lanhu-mcp`

## 3. 常用命令

### 查看命令帮助
```bash
python3 skills/lanhu-skill/scripts/bootstrap.py --help
```

### 识别链接类型
```bash
python3 skills/lanhu-skill/scripts/bootstrap.py classify-url --url "https://lanhuapp.com/web/#/item/project/product?tid=xxx&pid=xxx&docId=xxx"
```

### 获取页面列表
```bash
python3 skills/lanhu-skill/scripts/bootstrap.py get-pages --url "https://lanhuapp.com/web/#/item/project/product?tid=xxx&pid=xxx&docId=xxx"
```

### 分析页面
```bash
python3 skills/lanhu-skill/scripts/bootstrap.py analyze-pages --url "https://lanhuapp.com/web/#/item/project/product?tid=xxx&pid=xxx&docId=xxx" --page-names all --mode text_only
```

### 分析设计稿（支持统一评分模式）
```bash
python3 skills/lanhu-skill/scripts/bootstrap.py analyze-designs --url "https://lanhuapp.com/web/#/item/project/stage?tid=xxx&pid=xxx" --design-names "首页设计" --analysis-mode developer
```

## 4. 统一评分输出
- `analyze-pages` 与 `analyze-designs` 属于需求/设计分析命令，完成主体分析后必须输出统一研发评审评分表。
- 评分表规则来自 `references/rd-review-score-rubric.md`。
- 评分表字段、等级、决策口径必须固定，不得因分析模式不同而改变结构。
- `analyze-designs` 现支持 `--analysis-mode`，与页面分析共用同一套评分标准。

## 5. 退出码
- `0`：命令执行成功。
- `1`：参数错误、依赖缺失、或业务执行失败。

## 6. 环境约束
- `scripts/vendor/lanhu_impl.py` 来自上游 `lanhu-mcp` 的 vendor 版本。
- 首次真实执行时会在 `skills/lanhu-skill/.venv` 中自动安装依赖与 `chromium`。
- 若涉及截图和邀请链接解析，CLI 会直接使用 Playwright，而不是通过 MCP。
