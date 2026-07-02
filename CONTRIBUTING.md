# Contributing to java-development-skill

Thanks for considering a contribution! This is a personal skill, but PRs that improve accuracy, fill gaps, or fix real pain points are very welcome.

[English](#english) | [中文](#中文)

---

## English

### Ways to contribute

- **Fix a typo or unclear wording** — open a PR directly, no need to discuss first.
- **Fix an outdated rule** — Java/Spring evolves fast; if a rule no longer matches current behavior (e.g. a deprecated API was removed), PR the fix and note the version in the rule's `Context` section.
- **Add a new rule** — open an issue first to discuss scope. We keep the rule set focused; not every Java topic needs a rule.
- **Improve an example** — clearer code, better anti-pattern, more realistic scenario.

### Rule file structure (required for new rules)

Every rule file under `spring-boot/`, `code-review/`, `testing/`, `jvm/` must follow this structure:

```markdown
---
title: Short Rule Name
impact: HIGH | MEDIUM
impactDescription: one sentence on the concrete harm of getting it wrong
tags: relevant, comma, separated
description: one-sentence summary
alwaysApply: true   # optional, only for the most critical rules
---

## Short Rule Name

### Why it matters
(the concrete harm — not a generic "best practice" platitude)

### Correct
\`\`\`java
// example with explanation
\`\`\`

### Incorrect / When NOT to use
(either an anti-pattern, OR guidance on when the rule doesn't apply)

### Context
(version differences, edge cases, references, cross-refs to other rules)
```

Why this structure: it forces every rule to justify itself (`Why it matters`) and to be actionable (`Correct` / `Incorrect`). Rules without a concrete harm get rejected.

### Code style (applies to all examples)

Follow the project's [Code Style Baseline](README.md#-code-style-baseline):
- Constructor injection via `@RequiredArgsConstructor` (no field `@Autowired`)
- Lombok `@Slf4j` for logging
- `record` for DTOs, `@Data` for entities
- Spring Boot 3.x (`jakarta.*`) default; 2.x differences in `sb-migration-2-to-3.md`
- MyBatis-Plus as default persistence layer

### Workflow

1. Fork the repo, create a branch (`feat-add-stream-rule`, `fix-jpa-n-plus-1`, …).
2. Make your change. Keep diffs minimal — one rule or one fix per PR.
3. If adding a rule, update `SKILL.md`'s rule index table for the relevant domain.
4. Run `bash -n install.sh` if you touched the installer (syntax check).
5. Open a PR with a clear description: **what** changed, **why**, and **which file(s)**.

### What gets rejected

- Rules without a `Why it matters` that names a concrete harm.
- Examples that violate the code style baseline (field injection, `System.out.println`, etc.).
- Scope creep — a PR that touches 5 unrelated rules. Split it.
- Marketing language ("amazing", " revolutionary") — rules are technical, keep them dry.

### Commit message convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add stream parallelStream rule`
- `fix: correct Hibernate 6 UUID column type note`
- `docs: clarify Testcontainer reuse section`

---

## 中文

### 贡献方式

- **错别字 / 表述优化** —— 直接提 PR，无需事先讨论。
- **修正过时的规则** —— Java/Spring 演进很快，如果某条规则已不符合当前版本行为（比如某 API 被移除），提 PR 修正并在规则的 `Context` 里注明版本。
- **新增规则** —— 先开 issue 讨论范围。我们保持规则集聚焦，不是每个 Java 主题都需要一条规则。
- **改进示例** —— 更清晰的代码、更好的反例、更真实的场景。

### 规则文件结构（新增规则必填）

`spring-boot/`、`code-review/`、`testing/`、`jvm/` 下的每个规则文件必须遵循这个结构：

```markdown
---
title: 简短规则名
impact: HIGH | MEDIUM
impactDescription: 一句话说明错误的实际危害
tags: 相关, 逗号, 分隔
description: 一句话总结
alwaysApply: true   # 可选，仅用于最关键的规则
---

## 简短规则名

### Why it matters（为什么重要）
（具体的危害 —— 不要写"最佳实践"这种空话）

### Correct（正确做法）
\`\`\`java
// 带解释的示例
\`\`\`

### Incorrect / When NOT to use（反例 或 何时不用）
（要么是反模式，要么说明什么情况下这条规则不适用）

### Context（补充）
（版本差异、边界情况、参考资料、与其他规则的交叉引用）
```

为什么强制这个结构：它要求每条规则证明自己的价值（`Why it matters`），并保证可执行（`Correct` / `Incorrect`）。说不出具体危害的规则会被拒。

### 代码风格（所有示例适用）

遵循项目的[代码风格基线](README_zh.md#-代码风格基线)：
- 构造器注入 + `@RequiredArgsConstructor`（不要字段 `@Autowired`）
- 日志用 Lombok `@Slf4j`
- DTO 用 `record`，实体用 `@Data`
- 默认 Spring Boot 3.x（`jakarta.*`）；2.x 差异见 `sb-migration-2-to-3.md`
- 持久层默认 MyBatis-Plus

### 工作流

1. Fork 仓库，建分支（`feat-add-stream-rule`、`fix-jpa-n-plus-1` …）。
2. 改动。保持 diff 最小 —— 一个 PR 只做一条规则或一个修复。
3. 如果新增规则，在 `SKILL.md` 对应方向的规则索引表里加一行。
4. 如果改了安装器，跑 `bash -n install.sh` 做语法检查。
5. 提 PR，写清楚：**改了什么**、**为什么**、**哪些文件**。

### 会被拒绝的情况

- 没有 `Why it matters`、说不出具体危害的规则。
- 示例违反代码风格基线（字段注入、`System.out.println` 等）。
- 范围蔓延 —— 一个 PR 动了 5 条不相关的规则。拆开。
- 营销话术（"强大的"、"革命性的"）—— 规则是技术文档，保持克制。

### Commit message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：
- `feat: 新增 stream parallelStream 规则`
- `fix: 修正 Hibernate 6 UUID 列类型说明`
- `docs: 厘清 Testcontainer 复用章节`
