# Contributing

Thanks for improving `java-development`. Keep the skill useful for all Java developers, not only one framework stack.

## Principles

- General Java first; framework-specific rules only when the project uses that framework.
- Existing project conventions beat skill defaults.
- One focused change per PR: one rule, one fix, or one documentation update.
- Rules must be actionable, concise, and verifiable.
- Prefer automation for mechanical checks; use prose for judgment calls.

## Rule file structure

Every rule under `core/`, `build-tools/`, `spring-boot/`, `code-review/`, `testing/`, or `jvm/` must start with flat YAML frontmatter:

```markdown
---
title: Short Rule Name
impact: HIGH | MEDIUM | LOW
impactDescription: Concrete harm if this rule is ignored
tags: comma, separated, tags
description: One-sentence summary
---

## Short Rule Name

### Why it matters
Concrete harm, not generic best-practice language.

### Correct
Actionable guidance or a concise example.

### When NOT to use
Boundary conditions and cases where the rule should not be applied.

### Context
Version notes, references, and cross-refs to related rules.
```

Do not add `alwaysApply`. Route rules from `SKILL.md` so the agent loads only what the current task needs.

## Code style for examples

- Preserve the existing project stack and build tool.
- Do not introduce Spring Boot, Lombok, MyBatis-Plus, JPA, Testcontainers, or Java 17+ syntax unless the example explicitly targets that stack.
- In DI examples, prefer constructor injection.
- Use Lombok only in examples that state the project already uses Lombok.
- Use the existing logging facade; avoid production `System.out.println`.
- Preserve Maven/Gradle conventions such as BOMs, version catalogs, scopes, and toolchains.

## Validation

Run before opening a PR:

```powershell
python scripts/validate-skill.py

$venv = Join-Path $env:TEMP 'skill-validate-venv'
if (!(Test-Path $venv)) { python -m venv $venv }
& (Join-Path $venv 'Scripts\python.exe') -m pip install -q PyYAML
& (Join-Path $venv 'Scripts\python.exe') 'C:/Users/zd/.codex/skills/.system/skill-creator/scripts/quick_validate.py' 'D:/Java_project/ai_project/skills/java-development'
```

Also run `git diff --check` before publishing.

## What gets rejected

- Framework-first advice that applies Spring Boot/MyBatis-Plus/Lombok to unrelated Java projects.
- Rules without a concrete `Why it matters` / `impactDescription`.
- Broad rewrites, marketing language, or duplicated guidance already covered by another rule.
- Stale README/metadata counts after adding or removing rule files.

## Commit messages

Use Conventional Commits:

- `feat: add gradle build hygiene rule`
- `fix: clarify spring boot 4 migration baseline`
- `docs: update rule index counts`

---

# 贡献说明

感谢改进 `java-development`。这个 skill 的目标是服务所有 Java 开发者，而不是绑定某一个框架技术栈。

## 原则

- 先通用 Java，后框架专项；只有项目确实使用该框架时才加载框架规则。
- 现有项目约定优先于 skill 默认值。
- 一个 PR 只做一个聚焦改动：一条规则、一个修复或一次文档更新。
- 规则必须可执行、精简、可验证。
- 机械检查尽量自动化；需要判断的内容再写进文档。

## 规则文件结构

`core/`、`build-tools/`、`spring-boot/`、`code-review/`、`testing/`、`jvm/` 下的规则必须使用扁平 YAML frontmatter：

```markdown
---
title: 简短规则名
impact: HIGH | MEDIUM | LOW
impactDescription: 忽略该规则会造成的具体危害
tags: 逗号, 分隔, 标签
description: 一句话总结
---

## 简短规则名

### Why it matters（为什么重要）
具体危害，不写空泛最佳实践。

### Correct（正确做法）
可执行指导或简短示例。

### When NOT to use（何时不用）
适用边界和不该套用的情况。

### Context（补充）
版本差异、参考资料、相关规则。
```

不要添加 `alwaysApply`。统一通过 `SKILL.md` 路由，保证 Agent 只加载当前任务需要的规则。

## 示例代码风格

- 保留现有项目技术栈和构建工具。
- 不默认引入 Spring Boot、Lombok、MyBatis-Plus、JPA、Testcontainers 或 Java 17+ 语法，除非示例明确针对该技术栈。
- DI 示例优先构造器注入。
- Lombok 只用于明确“项目已使用 Lombok”的示例。
- 使用现有日志门面；生产代码避免 `System.out.println`。
- 保留 Maven/Gradle 的 BOM、版本目录、scope、toolchain 等约定。

## 校验

提交 PR 前运行：

```powershell
python scripts/validate-skill.py

$venv = Join-Path $env:TEMP 'skill-validate-venv'
if (!(Test-Path $venv)) { python -m venv $venv }
& (Join-Path $venv 'Scripts\python.exe') -m pip install -q PyYAML
& (Join-Path $venv 'Scripts\python.exe') 'C:/Users/zd/.codex/skills/.system/skill-creator/scripts/quick_validate.py' 'D:/Java_project/ai_project/skills/java-development'
```

同时运行 `git diff --check`。

## 会被拒绝的情况

- 把 Spring Boot/MyBatis-Plus/Lombok 强套到无关 Java 项目的框架优先建议。
- 没有具体 `Why it matters` / `impactDescription` 的规则。
- 大范围重写、营销话术、重复已有规则的内容。
- 新增/删除规则后 README/metadata 数量未同步。

## Commit message

使用 Conventional Commits：

- `feat: add gradle build hygiene rule`
- `fix: clarify spring boot 4 migration baseline`
- `docs: update rule index counts`
