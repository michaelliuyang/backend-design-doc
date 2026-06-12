# Backend Design Skills

面向后端研发流程的 Agent Skills 集合，用于从蓝湖原型需求分析到后端详细设计文档生成。

本仓库遵循 Agent Skills 的通用结构，可以通过 `npx skills` 安装到 Claude Code、Codex 以及其他兼容 Agent。仓库采用多 Skill 布局，所有 Skill 都放在 `skills/` 目录下。

也支持 Claude Code plugin marketplace：仓库内包含 `.claude-plugin/marketplace.json`，可以通过 Claude Code 的 `/plugin marketplace add` 和 `/plugin install` 安装。

## Skills

### lanhu-skill

基于蓝湖 Lanhu PRD、原型、页面树、设计稿或邀请链接做需求分析。

适用于：

- 分析蓝湖原型需求。
- 梳理页面流程、业务规则、异常分支和数据对象。
- 识别产品材料中的概念混乱、规则冲突和待确认事项。
- 生成后续 `$write-design-doc` 可直接使用的需求分析输入。

### write-design-doc

基于需求分析、PRD、概要设计、架构草稿、现有代码、DDL 或 API 文档，生成后端详细设计文档。

适用于：

- 将需求分析或概要设计转成可评审的后端详细设计文档。
- 设计或评审 Java/Spring 后端实现方案。
- 生成 API 设计、DDL 草案、错误码映射、事务边界和兼容方案。
- 把复杂需求整理成可直接交给 AI Coding Agent 的实施输入。

## 推荐流程

```text
蓝湖原型PRD
  -> lanhu-skill
  -> 需求分析文档 / 概要设计 或 方案分析
  -> write-design-doc
  -> 后端详细设计文档
  -> AI Coding 输入
```

## 安装

### npx skills

从 GitHub 仓库安装全部 Skills：

```bash
npx skills add michaelliuyang/backend-design-doc --all
```

只安装到 Claude Code 和 Codex：

```bash
npx skills add michaelliuyang/backend-design-doc --skill '*' -a claude-code -a codex
```

只安装某一个 Skill：

```bash
npx skills add michaelliuyang/backend-design-doc --skill lanhu-skill
npx skills add michaelliuyang/backend-design-doc --skill write-design-doc
```

只安装到 Claude Code，全局安装并跳过确认：

```bash
npx skills add michaelliuyang/backend-design-doc -a claude-code -g -y
```

### Claude Code Plugin

在 Claude Code 中添加本仓库作为 plugin marketplace：

```text
/plugin marketplace add michaelliuyang/backend-design-doc
```

安装完整插件：

```text
/plugin install backend-design-skills@backend-design-doc
```

也可以只安装单个插件入口：

```text
/plugin install lanhu-skill@backend-design-doc
/plugin install write-design-doc@backend-design-doc
```

## 手动安装
### Codex

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/backend-design-doc/skills/lanhu-skill ~/.codex/skills/
cp -R /path/to/backend-design-doc/skills/write-design-doc ~/.codex/skills/
```

## 文件结构

```text
backend-design-doc/
├── .claude-plugin/
│   └── marketplace.json
├── README.md
└── skills/
    ├── lanhu-skill/
    │   ├── SKILL.md
    │   └── references/
    └── write-design-doc/
        ├── SKILL.md
        └── references/
```

## 文件说明

- `SKILL.md`：每个 Skill 的入口，定义触发场景、工作流程、输出要求和交付门禁。
- `references/`：按需加载的详细规则、模板和工作流说明。
- `.claude-plugin/marketplace.json`：Claude Code plugin marketplace 入口，声明整包插件和单 Skill 插件入口。

## 使用示例

```text
使用 lanhu-skill，分析这个蓝湖原型链接，并输出后端设计输入摘要。
```

```text
使用 write-design-doc，基于这份需求分析文档，生成后端详细设计文档。
```

```text
先用 lanhu-skill 分析蓝湖原型，再用 write-design-doc 生成后端详细设计。
```
