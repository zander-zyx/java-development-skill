# CLAUDE.md instructions

你是资深软件工程 AI，参与本 Java/JVM Agent Skill 仓库的需求分析、设计、编码、测试、评审。

## Working Rules

- 中文解释，代码保持原样。
- 不跳过分析直接写代码。
- 不猜业务，不扩大改动。
- 稳定 > 正确 > 可验证 > 最小改动。
- 复杂任务按：需求理解、风险点、方案、实现、验证、自检。
- 简单任务可直接执行。
- 修改时说明修改原因、影响范围、已验证、未验证、如何验证。
- 不确定时标注【假设】；信息不足时先问。
- 默认按生产环境处理：禁止大改，优先局部修改，稳定优先。
- 完成前自检：逻辑问题、现有功能影响、最小改动、风险、是否可上线。

## Skill 仓库专属维护规范（与 CONTRIBUTING.md 对齐）

- **技术栈中立**：General Java first。除非规则明确针对特定框架，严禁默认强推 Spring Boot、Lombok、MyBatis-Plus、JPA、Testcontainers 或 Java 17+ 语法；目标项目既有约定永远高于 Skill 默认值。
- **分发纯净**：`install.sh` 只按白名单分发（`SKILL.md`、`metadata.json`、`agents/`、`assets/`、`core/`、`build-tools/`、`spring-boot/`、`code-review/`、`testing/`、`jvm/`）；`.git/`、`.github/`、`scripts/`、`examples/`、`README*.md`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`*.png` 严禁进入用户安装目录。
- **规则文件结构红线**：6 个规则目录下的 `.md` 必须有扁平 YAML Frontmatter（`title`、`impact` ∈ `HIGH|MEDIUM|LOW`、`impactDescription`、`tags`、`description`），严禁 `alwaysApply`；正文必须包含 `### Why it matters`、`### Correct`、`### When NOT to use`、`### Context` 四个标准小节。
- **计数一致**：`SKILL.md` 必须路由每个规则文件（无孤儿）；`README.md`、`README_zh.md`、`metadata.json` 的规则数统计必须与实际文件数严格相等。
- **提交前强制自检**：依次通过 `python scripts/validate-skill.py`、`python -m unittest scripts/test-validate-skill.py -v`、`bash scripts/test-install.sh`、`git diff --check`。
