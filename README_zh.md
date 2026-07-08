# Java Development Skill（Java 开发技能包）

[![Java](https://img.shields.io/badge/Java-17%2F21-orange.svg)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![MyBatis-Plus](https://img.shields.io/badge/MyBatis--Plus-3.5%2B-red.svg)](https://baomidou.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#-许可证)
[![Rules](https://img.shields.io/badge/rules-26-success.svg)](#-规则索引)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-兼容-7c3aed.svg)](#-安装)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-兼容-412991.svg)](#-安装)
[![OpenCode](https://img.shields.io/badge/OpenCode-兼容-ff7f0e.svg)](#-安装)

[English](./README.md) | **中文**

> 一个统一的 **AI Agent 技能包**，覆盖 Java + Spring Boot 工程的方方面面 —— 开发规范、代码审查、测试、JVM 排障。适用于 Claude Code / OpenAI Codex / OpenCode / ZCode，以及任何支持 SKILL.md 规范的 Agent。

---

## 📑 目录

- [📖 这是什么](#-这是什么) · [🎯 为什么要用 skill](#-为什么要用-skill) · [✨ 特性亮点](#-特性亮点)
- [📂 项目结构](#-项目结构) · [🚀 安装](#-安装) · [💡 怎么使用](#-怎么使用)
- [🛠 故障排查](#-故障排查) · [🎨 代码风格基线](#-代码风格基线) · [📑 规则索引](#-规则索引)
- [🤝 如何贡献](#-如何贡献) · [📜 许可证](#-许可证)

---

## 📖 这是什么

一个把 AI 编码助手变成**资深 Java/Spring Boot 工程师**的知识库。它不依赖模型自身的通用 Java 知识，而是注入经过筛选、有明确立场的最佳实践 —— 就是那种高级工程师在代码审查时会强制执行的规则。

技能围绕**4 个真实工程场景**组织，采用**渐进式信息披露（Progressive Disclosure）**设计：

- `SKILL.md` 是 skill 触发后加载的轻量路由文件 —— 包含默认约定、加载预算和路由表。
- 具体规则文件**按需加载**，只在任务匹配时才读取。这样既保持每一轮对话的精简，又能容纳 26 条深度规则。

这模拟了人类工程师的工作方式：你不会每次写方法前都重读一遍《Effective Java》—— 而是在用到时查阅具体规则。

## ✨ 特性亮点

- **🎯 国内生态优先** —— MyBatis-Plus 作为默认持久层（JPA 作为可选参考），贴合国内 Spring Boot 项目的主流技术栈。
- **🏗 4 大方向，26 条规则** —— Spring Boot 开发、Java 代码审查、Java 测试、JVM 排障。
- **📐 统一的代码风格** —— 构造器注入 + Lombok 必要项（`@RequiredArgsConstructor` / `@Slf4j` / `@Data`），所有示例保持一致。
- **🔄 版本感知** —— 默认 Spring Boot 3.x（`jakarta.*`、Java 17+），并提供专门的迁移指南覆盖 2.x 到 3.x 的 6 大破坏性变更。
- **📋 即拷即用的模板** —— Maven pom（SB2/SB3）、Controller-Service-Test 三层骨架、多环境 `application.yml`。
- **🔍 适合代码审查** —— 每条 code-review 规则都包含可执行的检查清单，你可以自己心算，也可以让 Agent 跑。

## 🎯 为什么要用 skill

现在的 LLM 本来就"懂" Java，那为什么还要装这个 skill？因为通用知识是**没立场的**、**每次回答不一致** —— 模型今天用字段注入、明天又用构造器注入。这个 skill 锁定**一套连贯的约定**，并在对的时刻浮现对的规则。

| 没有 skill | 有这个 skill |
|-----------|--------------|
| 模型按心情挑注入方式 | 永远构造器注入 + `@RequiredArgsConstructor` |
| 漏掉 checked exception 的 `@Transactional(rollbackFor=Exception.class)` | 规则自动套用 |
| 用 H2 来"测"MyBatis 的 SQL | 用 Testcontainers + 真实 MySQL |
| 泛泛的"注意线程安全"建议 | 逐条跑 `code-review/cr-concurrency.md` 的检查清单 |
| 猜 SB 2.x 还是 3.x 的行为 | 加载 `spring-boot/sb-migration-2-to-3.md`，给出 6 大破坏性变更 |
| 抄来过时的 Lombok 建议（`@AllArgsConstructor`） | 限制在 Lombok 白名单内 |

Skill 的价值，就是"会写 Java 的 AI"和"按你团队规范写 Java 的 AI"之间的差距。

### 前置条件

安装 skill 之前，你需要 **Git** 和**至少一个支持的 AI 工具**。Skill 只是给 Agent 的知识，它本身不需要 Java 或 JDK（你的 Java 项目才需要）。

| 前置项 | 检查是否已装 | 安装方式 |
|--------|-------------|---------|
| **Git** | `git --version` | [git-scm.com](https://git-scm.com/downloads) |
| **Claude Code** | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| **OpenAI Codex** | `codex --version` | [developers.openai.com/codex](https://developers.openai.com/codex) |
| **OpenCode** | `opencode --version` | [opencode.ai/docs](https://opencode.ai/docs/) |
| **ZCode** | 检查 `~/.zcode/` 是否存在 | 你的 ZCode 发行渠道 |

四个工具里装**一个**就够了，挑你已经在用的。

## 📂 项目结构

```
java-development-skill/
├── SKILL.md                # 路由文件：加载预算 + 路由表（触发后加载）
├── README.md               # 英文说明
├── README_zh.md            # 中文说明（本文件）
├── AGENTS.md               # Codex/OpenCode 类 Agent 的常驻工程纪律
├── CLAUDE.md               # Claude Code 的常驻工程纪律
├── metadata.json           # 版本元数据
├── agents/openai.yaml      # OpenAI/Codex UI 元数据
│
├── spring-boot/            # 🌱 方向 A —— Spring Boot 开发（9 条规则）
│   ├── sb-dependency-injection.md      构造器注入 + Lombok 策略
│   ├── sb-project-structure.md         按特性分包的分层结构
│   ├── sb-config-profiles.md           application.yml + profile + 密钥管理
│   ├── sb-mybatis-plus.md       ⭐    BaseMapper/IService、分页、逻辑删除（默认）
│   ├── sb-jpa-repository.md           JPA：N+1、@Transactional、Hibernate 6 UUID（可选）
│   ├── sb-exception-handling.md       @RestControllerAdvice + RFC 7807 ProblemDetail
│   ├── sb-rest-client.md              RestClient（新）vs RestTemplate（已弃用）
│   ├── sb-actuator-health.md          Actuator + Micrometer + 链路追踪
│   └── sb-migration-2-to-3.md  ⭐    SB 2.x ↔ 3.x 迁移（6 大关键差异）
│
├── code-review/            # 🔍 方向 B —— Java 代码审查（6 条规则）
│   ├── cr-concurrency.md              synchronized、锁、竞态条件
│   ├── cr-resource-leak.md            try-with-resources、连接关闭
│   ├── cr-null-safety.md              Optional、@Nullable、NPE 防御
│   ├── cr-equals-hashcode.md          equals/hashCode 契约、Record
│   ├── cr-stream-pitfalls.md          并行流、流复用、共享可变状态
│   └── cr-anti-patterns.md            魔法值、异常吞噬、日志滥用
│
├── testing/                # 🧪 方向 C —— Java 测试（6 条规则）
│   ├── test-layering.md               单元/切片/集成测试分层金字塔
│   ├── test-junit5.md                 JUnit 5 生命周期、参数化、扩展
│   ├── test-mockito.md                桩件、验证、spy、静态 mock
│   ├── test-testcontainers.md  ⭐    @ServiceConnection、真实 DB 边界
│   ├── test-spring-boot-test.md       @WebMvcTest / @DataJpaTest / @SpringBootTest
│   └── test-coverage-assertj.md       AssertJ 流式断言 + JaCoCo 覆盖率
│
├── jvm/                    # 🔥 方向 D —— JVM 排障（5 条规则）
│   ├── jvm-gc-tuning.md               G1 / ZGC / Parallel 选型与调优
│   ├── jvm-oom-analysis.md            OOM 堆 dump + MAT 支配树分析
│   ├── jvm-thread-dump.md             死锁检测、阻塞线程、线程泄漏
│   ├── jvm-cpu-high.md                top -Hp + jstack + async-profiler 火焰图
│   └── jvm-gc-logs.md                 -Xlog:gc* 日志解读
│
└── assets/                 # 📋 即拷即用模板
    ├── pom-spring-boot-3.xml           SB3 pom（Java 17、jakarta、MyBatis-Plus）
    ├── pom-spring-boot-2.xml           SB2 pom（javax、旧项目维护）
    ├── controller-service-test.java    Controller + Service + Mapper + Test 骨架
    └── application.yml.template        多环境配置（dev/prod profile）

examples/                  # 💡 实际效果演示
    ├── usage-examples.md              真实 prompt + skill 的输出（英文）
    └── usage-examples.zh.md           中文版
```

⭐ = 影响最大的规则，建议优先阅读。

## 🚀 安装

本 skill 兼容**四款 AI 编码工具**。`SKILL.md` 遵循新兴的 [agentskills.io](https://agentskills.io) 标准 —— 同一份内容能在所有工具里加载，只是每个工具查找的目录不同。

### 适配矩阵

| Agent/工具 | Skill 入口 | 常驻指令 | UI 元数据 | 安装路径 |
|------------|------------|----------|-----------|----------|
| Claude Code | `SKILL.md` | `CLAUDE.md` | frontmatter | `~/.claude/skills/java-development` |
| OpenAI Codex | `SKILL.md` | `AGENTS.md` | `agents/openai.yaml` | `~/.codex/skills/java-development` |
| OpenCode | `SKILL.md` | `AGENTS.md` | frontmatter | `~/.config/opencode/skills/java-development` |
| ZCode | `SKILL.md` | `SKILL.md` 默认约定 | frontmatter | `~/.zcode/skills/java-development` |

`SKILL.md` 是 Java 路由的共同事实源。`AGENTS.md` 和 `CLAUDE.md` 只承载工具专属的常驻工程纪律，让 Codex/OpenCode 和 Claude Code 在 skill 触发前也尽量保持一致。

### 前置条件

安装 skill 之前，你需要 **Git** 和**至少一个支持的 AI 工具**。Skill 只是给 Agent 的知识，它本身不需要 Java 或 JDK（你的 Java 项目才需要）。

| 前置项 | 检查是否已装 | 安装方式 |
|--------|-------------|---------|
| **Git** | `git --version` | [git-scm.com](https://git-scm.com/downloads) |
| **Claude Code** | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| **OpenAI Codex** | `codex --version` | [developers.openai.com/codex](https://developers.openai.com/codex) |
| **OpenCode** | `opencode --version` | [opencode.ai/docs](https://opencode.ai/docs/) |
| **ZCode** | 检查 `~/.zcode/` 是否存在 | 你的 ZCode 发行渠道 |

四个工具里装**一个**就够了，挑你已经在用的。

### 方式一：一键安装脚本（推荐）

脚本会自动检测你装了哪四个工具中的哪些，并把 skill 软链接到各自的发现目录。

```bash
# 1. 克隆仓库
git clone https://github.com/zander-zyx/java-development-skill.git

# 2. 进入目录
cd java-development-skill

# 3. 运行安装脚本
./install.sh
```

**预期输出**（你装了几个工具就有几行）：
```
✓ claude: linked → /Users/你/.claude/skills/java-development
✓ codex:  linked → /Users/你/.codex/skills/java-development
Done. The 'java-development' skill is now active in the tools above.
Restart any running tool sessions to pick it up.
```

脚本参数：
- `./install.sh --force` —— 覆盖已有安装（换了 clone 源后重新链接等）
- `./install.sh --uninstall` —— 从所有检测到的工具移除 skill
- `./install.sh --help` —— 查看用法

> **所在区域慢？** 先从镜像克隆，再跑同一个脚本：
> ```bash
> git clone https://gitee.com/zdking_project/java-development-skill.git   # Gitee（国内）
> # 或：https://cnb.cool/zdking/java-development-skill                    # cnb.cool
> cd java-development-skill && ./install.sh
> ```

> **Windows 用户**：请在 **Git Bash** 或 **WSL** 里运行脚本（不要用 cmd.exe / PowerShell）。Git Bash 随 Git for Windows 自带。如果软链接步骤回退成复制，也没问题 —— 之后用 `git pull && ./install.sh --force` 更新即可。

### 方式二：让 AI 工具帮你装（不用开终端）

你本来就在用 AI 编码助手 —— 最省事的方式是直接让它帮你装 skill。在 Claude Code / Codex / OpenCode / ZCode 里打开对话，粘贴：

```
帮我安装 java-development skill，地址 https://github.com/zander-zyx/java-development-skill
装到你的 skill 目录里，然后确认加载成功。
```

Agent 会自动 `git clone` 到它自己的 skill 目录、确认 `SKILL.md` 就位、然后告诉你装好了。你不需要知道路径，也不用敲任何命令。

**Agent 会做什么**（让你心里有数）：
1. 把仓库 clone 到该工具的 skills 目录（比如 `~/.claude/skills/java-development/`）。
2. 列目录确认 `SKILL.md` 存在。
3. 报告成功 —— 你重启会话（或它自动重载）后 skill 即生效。

**更省事 —— 每个工具一行话：**

| 工具 | 把这句粘贴到对话里 |
|------|-------------------|
| Claude Code | `把 https://github.com/zander-zyx/java-development-skill clone 到 ~/.claude/skills/java-development，确认 SKILL.md 在。` |
| Codex | `把 https://github.com/zander-zyx/java-development-skill clone 到 ~/.codex/skills/java-development，确认 SKILL.md 在。` |
| OpenCode | `把 https://github.com/zander-zyx/java-development-skill clone 到 ~/.config/opencode/skills/java-development，确认 SKILL.md 在。` |
| ZCode | `把 https://github.com/zander-zyx/java-development-skill clone 到 ~/.zcode/skills/java-development，确认 SKILL.md 在。` |

> 如果 GitHub 慢，告诉 Agent 用镜像：`https://gitee.com/zdking_project/java-development-skill.git`（国内）或 `https://cnb.cool/zdking/java-development-skill`。

### 方式三：手动安装到单个工具

不想跑脚本的话，直接把仓库 clone 到工具的 skill 目录。每个工具在 home 下的目录不同：

| 工具 | skill 路径 | 命令 |
|------|-----------|------|
| **Claude Code** | `~/.claude/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.claude/skills/java-development` |
| **OpenAI Codex** | `~/.codex/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.codex/skills/java-development` |
| **OpenCode** | `~/.config/opencode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.config/opencode/skills/java-development` |
| **ZCode** | `~/.zcode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.zcode/skills/java-development` |

这一条 `git clone` 就是完整安装，没有构建步骤，不用改配置。

### 方式四：项目级安装（只在一个项目里生效）

只想让 skill 在某个 Java 项目里生效、不要全局？克隆到该项目的本地工具目录：

```bash
# 在你的 Java 项目根目录里，按你的工具选其一：
git clone https://github.com/zander-zyx/java-development-skill.git .claude/skills/java-development
# 或：  .codex/skills/java-development
#       .zcode/skills/java-development
#       .config/opencode/skills/java-development
```

项目级 skill 优先级高于用户级，所以这种方式还能针对单个项目覆盖全局安装。

### 方式五：不装任何工具，纯阅读

`*.md` 文件都是纯 Markdown。可以直接在 GitHub/Gitee/cnb 上浏览，或 clone 下来本地看。把单条规则复制到团队 Wiki 也行。不需要任何 AI 工具。

### 验证安装是否成功

**30 秒检查** —— 在工具里开个新会话（skill 是启动时加载的，所以如果工具已经开着，先重启），粘贴：

```
JPA 里怎么避免 N+1 查询？
```

你应该得到明确提到 **JOIN FETCH / EntityGraph** 和 `open-in-view = false` 的答案 —— 这些来自 `spring-boot/sb-jpa-repository.md`。如果答案很泛泛（"用懒加载…"），说明 skill 没加载，看下面的[故障排查](#-故障排查)。

## 💡 怎么使用

你不需要"打开"或"调用" skill。安装后，它在每次 Java 相关对话中**透明地**在后台工作。

### 心智模型

```
你输入一个 Java 问题
        │
        ▼
工具读取 SKILL.md 的 description（触发元数据）
        │
        ├── 关键词命中（@RestController、OOM、MyBatis-Plus …）
        │     └── 工具加载 SKILL.md 的轻量路由表
        │           └── 只加载当前任务需要的具体规则文件
        │                 └── 答案遵循对应规则的约定
        │
        └── 没命中 → 工具用通用知识回答（skill 保持沉默）
```

你永远不会敲文件名。skill 根据你说的话决定加载什么。

### 在哪里用

- **在你的 Java 项目里** —— `cd` 进项目，在那里启动工具。它既能看到你的 `pom.xml` / 源码，又加载了 skill。效果最好。
- **任意目录** —— skill 是用户级全局的（方式一/二之后）。即使在项目外问 Java 问题，skill 也生效，只是工具看不到你的代码。

### 问什么 —— 触发示例

`SKILL.md` 的 `description` 字段捕获 Java/Spring/JVM 相关信号；触发后由路由表选择最小可用规则集。一些能命中 skill 的自然 prompt：

| 你说…… | 技能加载…… |
|--------|-----------|
| *"写个 Order 的 JPA repository，注意 N+1"* | `spring-boot/sb-jpa-repository.md`（→ JOIN FETCH / EntityGraph） |
| *"我的 MyBatis-Plus 分页返回了全部数据"* | `spring-boot/sb-mybatis-plus.md`（→ 漏配 `PaginationInnerInterceptor`） |
| *"帮我审查这个类的线程安全"* | `code-review/cr-concurrency.md` + `code-review/cr-resource-leak.md` |
| *"用 Testcontainers 配 MySQL"* | `testing/test-testcontainers.md`（→ `@ServiceConnection`） |
| *"线上 OOM 了，怎么定位泄漏？"* | `jvm/jvm-oom-analysis.md`（→ 堆 dump + MAT） |
| *"从 Spring Boot 2.7 迁移到 3"* | `spring-boot/sb-migration-2-to-3.md`（→ 6 大破坏性变更） |
| *"帮我写个 OrderService，保存订单+调支付"* | `spring-boot/sb-dependency-injection.md` + `spring-boot/sb-mybatis-plus.md`（中文也触发） |

完整 prompt 和实际输出见 [`examples/usage-examples.zh.md`](examples/usage-examples.zh.md)（或 [英文版](examples/usage-examples.md)）。

### 自动触发没命中时，强制加载

如果某个 prompt 本该触发却没触发（少见，通常是措辞太特殊），手动强制：

| 工具 | 命令 |
|------|------|
| **Claude Code** | `/skill java-development` 然后输入你的 prompt（或下次提到 Java 时自动加载） |
| **Codex** | `/skill java-development <你的 prompt>` |
| **ZCode** | `/skill java-development <你的 prompt>` |
| **OpenCode** | 已安装的 skill 由触发元数据加载；换个带 description 关键词的说法 |

### 保持 skill 更新

skill 会持续迭代。拉取新规则和更新：

```bash
cd ~/.claude/skills/java-development    # 或你 clone 的位置
git pull
```

如果你用了安装脚本（软链接方式），在原始 clone 目录 `git pull` 会**一次性更新所有工具** —— 它们共享同一份源码。

## 🛠 故障排查

| 症状 | 可能原因 | 解决 |
|------|---------|------|
| 问 Java 问题 skill 没触发 | 安装时工具会话已经开着 | 重启工具（skill 是启动时加载的） |
| `./install.sh: Permission denied` | 脚本没有执行权限 | `chmod +x install.sh` 后重试 |
| 脚本报 "No AI tool config directories found" | `.claude` / `.codex` / `.config/opencode` / `.opencode` / `.zcode` 都不存在 | 先装一个工具（见[前置条件](#前置条件)），或用 `./install.sh --force` 创建路径 |
| Windows：`ln: failed to create symbolic link` | 没有软链接权限 | 脚本会自动回退到复制；或用管理员身份运行 Git Bash |
| `git pull` 提示 "detached HEAD" | 进错目录了 | 安装脚本用的是软链接；`cd` 到原始 clone 目录（软链接指向的目标）去 pull，而不是链接本身 |
| Codex/OpenCode 加载了 skill 但不遵循规则 | 这类工具用 `AGENTS.md` 做常驻指令，用 `SKILL.md` 做按需路由 | 这是设计如此；换个 Java/Spring/JVM 触发关键词 |
| 更新了仓库但工具还用旧规则 | 工具按会话缓存 skill | 重启工具会话 |

如果遇到其他问题，[提个 issue](https://github.com/zander-zyx/java-development-skill/issues)，附上工具名、操作系统、以及具体命令和输出。

## 🎨 代码风格基线

本技能里所有示例都遵循统一约定，保证生成的代码风格一致：

| 方面 | 约定 |
|------|------|
| **依赖注入** | 构造器注入，通过 `final` 字段 + `@RequiredArgsConstructor`（绝不字段 `@Autowired`） |
| **日志** | Lombok `@Slf4j` + SLF4J（绝不 `System.out.println`） |
| **DTO** | Java `record`（不可变，无需 Lombok） |
| **实体** | Lombok `@Data`（可变，配合基于 id 的 `equals`/`hashCode` —— 见 `code-review/cr-equals-hashcode.md`） |
| **持久层** | **MyBatis-Plus** 为默认（国内主流）；JPA 作为可选参考 |
| **Spring Boot** | 3.x（`jakarta.*`、Java 17+）；2.x 差异见 `spring-boot/sb-migration-2-to-3.md` |
| **构建工具** | Maven |

## 📑 规则索引

<details>
<summary><b>🌱 Spring Boot 开发（9 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `spring-boot/sb-dependency-injection.md` | HIGH | 构造器注入、Lombok 白名单、Bean 生命周期 |
| `spring-boot/sb-project-structure.md` | HIGH | 按特性分包的分层结构 |
| `spring-boot/sb-config-profiles.md` | MEDIUM | application.yml、profile、`spring.config.import` |
| `spring-boot/sb-mybatis-plus.md` ⭐ | HIGH | BaseMapper/IService、LambdaQueryWrapper、分页、逻辑删除 |
| `spring-boot/sb-jpa-repository.md` | MEDIUM | N+1、@Transactional、懒加载、Hibernate 6 UUID |
| `spring-boot/sb-exception-handling.md` | HIGH | @RestControllerAdvice、RFC 7807 ProblemDetail |
| `spring-boot/sb-rest-client.md` | MEDIUM | RestClient vs RestTemplate（已弃用）vs WebClient |
| `spring-boot/sb-actuator-health.md` | MEDIUM | Actuator、Micrometer、分布式链路追踪 |
| `spring-boot/sb-migration-2-to-3.md` ⭐ | HIGH | 2.x ↔ 3.x 迁移（6 大破坏性变更） |

</details>

<details>
<summary><b>🔍 Java 代码审查（6 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `code-review/cr-concurrency.md` | HIGH | synchronized、锁、竞态条件、原子类、虚拟线程 |
| `code-review/cr-resource-leak.md` | HIGH | try-with-resources、流、连接、锁 |
| `code-review/cr-null-safety.md` | HIGH | Optional 用法、@Nullable、NPE 防御 |
| `code-review/cr-equals-hashcode.md` | MEDIUM | equals/hashCode 契约、Record、实体相等性 |
| `code-review/cr-stream-pitfalls.md` | MEDIUM | 并行流、流复用、共享可变状态 |
| `code-review/cr-anti-patterns.md` | MEDIUM | 魔法值、异常吞噬、日志滥用 |

</details>

<details>
<summary><b>🧪 Java 测试（6 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `testing/test-layering.md` | HIGH | 单元/切片/集成测试金字塔 |
| `testing/test-junit5.md` | HIGH | JUnit 5 生命周期、参数化测试、扩展 |
| `testing/test-mockito.md` | HIGH | 桩件/验证、参数匹配器、静态 mock |
| `testing/test-testcontainers.md` ⭐ | HIGH | @ServiceConnection、真实 DB 边界、容器复用 |
| `testing/test-spring-boot-test.md` | HIGH | @WebMvcTest / @DataJpaTest / @SpringBootTest 切片 |
| `testing/test-coverage-assertj.md` | MEDIUM | AssertJ 流式断言、JaCoCo 覆盖率 |

</details>

<details>
<summary><b>🔥 JVM 排障（5 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `jvm/jvm-gc-tuning.md` | HIGH | G1 / ZGC / Parallel 选型、堆内存设置 |
| `jvm/jvm-oom-analysis.md` | HIGH | OOM 自动 dump、MAT 支配树、泄漏模式 |
| `jvm/jvm-thread-dump.md` | HIGH | 死锁检测、阻塞线程、线程泄漏 |
| `jvm/jvm-cpu-high.md` | HIGH | top -Hp + jstack + async-profiler 火焰图 |
| `jvm/jvm-gc-logs.md` | MEDIUM | -Xlog:gc* 解读、GCEasy |

</details>

## 🤝 如何贡献

这是个人技能包，但欢迎 PR。完整指南见 **[CONTRIBUTING.md](CONTRIBUTING.md)**（规则文件结构、代码风格、commit 规范，中英双语）。

快速摘要：

1. **错别字 / 表述优化** —— 直接提 PR，无需讨论。
2. **新增规则** —— 先开 issue 讨论范围。遵循现有文件结构：frontmatter（`title` / `impact` / `tags` / `description`）+ 章节（`Why it matters` / `Correct` / `Incorrect` / `Context`）。
3. **框架行为更新** —— Java/Spring 演进很快。如果某条规则在当前版本已过时，提 PR 修正并在 `Context` 里注明版本。

本项目遵循 [Contributor Covenant 行为准则](CODE_OF_CONDUCT.md)。参与即表示你同意遵守其条款。

技能编写时对齐的版本见 `metadata.json`。

## 📜 许可证

MIT —— 见 [LICENSE](LICENSE)。可自由使用、修改、分发。注明出处感谢但不强制。

---

**编写时间**：2026 年 7 月 · **目标版本**：Spring Boot 3.x + Java 17/21 · **默认持久层**：MyBatis-Plus
