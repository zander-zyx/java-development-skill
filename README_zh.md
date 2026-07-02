# Java Development Skill（Java 开发技能包）

[![Java](https://img.shields.io/badge/Java-17%2F21-orange.svg)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![MyBatis-Plus](https://img.shields.io/badge/MyBatis--Plus-3.5%2B-red.svg)](https://baomidou.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#-许可证)
[![Rules](https://img.shields.io/badge/rules-26-success.svg)](#-规则索引)

[English](./README.md) | **中文**

> 一个统一的 **AI Agent 技能包**，覆盖 Java + Spring Boot 工程的方方面面 —— 开发规范、代码审查、测试、JVM 排障。适用于 ZCode / Claude Code / 任何支持 SKILL.md 规范的 Agent。

---

## 📖 这是什么

一个把 AI 编码助手变成**资深 Java/Spring Boot 工程师**的知识库。它不依赖模型自身的通用 Java 知识，而是注入经过筛选、有明确立场的最佳实践 —— 就是那种高级工程师在代码审查时会强制执行的规则。

技能围绕**4 个真实工程场景**组织，采用**渐进式信息披露（Progressive Disclosure）**设计：

- `SKILL.md`（路由文件）始终在 Agent 上下文中 —— 一个轻量的决策树 + 索引。
- 具体规则文件**按需加载**，只在任务匹配时才读取。这样既保持每一轮对话的精简，又能容纳 26 条深度规则。

这模拟了人类工程师的工作方式：你不会每次写方法前都重读一遍《Effective Java》—— 而是在用到时查阅具体规则。

## ✨ 特性亮点

- **🎯 国内生态优先** —— MyBatis-Plus 作为默认持久层（JPA 作为可选参考），贴合国内 Spring Boot 项目的主流技术栈。
- **🏗 4 大方向，26 条规则** —— Spring Boot 开发、Java 代码审查、Java 测试、JVM 排障。
- **📐 统一的代码风格** —— 构造器注入 + Lombok 必要项（`@RequiredArgsConstructor` / `@Slf4j` / `@Data`），所有示例保持一致。
- **🔄 版本感知** —— 默认 Spring Boot 3.x（`jakarta.*`、Java 17+），并提供专门的迁移指南覆盖 2.x 到 3.x 的 6 大破坏性变更。
- **📋 即拷即用的模板** —— Maven pom（SB2/SB3）、Controller-Service-Test 三层骨架、多环境 `application.yml`。
- **🔍 适合代码审查** —— 每条 code-review 规则都包含可执行的检查清单，你可以自己心算，也可以让 Agent 跑。

## 📂 项目结构

```
java-development-skill/
├── SKILL.md                # 路由文件：决策树 + 规则索引（始终加载）
├── README.md               # 英文说明
├── README_zh.md            # 中文说明（本文件）
├── metadata.json           # 版本元数据
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
```

⭐ = 影响最大的规则，建议优先阅读。

## 🚀 快速开始

### 方式一：作为 ZCode / Claude Code 技能安装

ZCode 在以下目录发现技能（优先级从高到低）：

- `<项目>/.zcode/skills/<名称>/SKILL.md`
- `~/.zcode/skills/<名称>/SKILL.md`         ← 个人使用推荐
- `~/.agents/skills/<名称>/SKILL.md`

```bash
# 克隆到用户级技能目录
git clone https://github.com/zander-zyx/java-development-skill.git ~/.zcode/skills/java-development
```

完成。下次你向 Agent 提问 Java / Spring Boot 相关问题时，它会自动加载相关规则。

### 方式二：项目级安装（仅当前仓库生效）

```bash
# 在你的 Java 项目内
git clone https://github.com/zander-zyx/java-development-skill.git .zcode/skills/java-development
```

### 方式三：当作文档阅读

`*.md` 文件都是纯 Markdown —— 可以直接当作复习资料阅读，或把单条规则复制到团队 Wiki。

## 💡 使用示例

安装后，Agent 会根据上下文自动选择正确的规则。你不需要记文件名。

| 你说…… | 技能加载…… |
|--------|-----------|
| *"写个 Order 的 JPA repository，注意 N+1"* | `sb-jpa-repository.md`（N+1 → JOIN FETCH / EntityGraph） |
| *"我的 MyBatis-Plus 分页返回了全部数据"* | `sb-mybatis-plus.md`（漏配 `PaginationInnerInterceptor`） |
| *"帮我审查这个类的线程安全"* | `cr-concurrency.md` + `cr-resource-leak.md` |
| *"用 Testcontainers 配 MySQL"* | `test-testcontainers.md`（`@ServiceConnection`） |
| *"线上 OOM 了，怎么定位泄漏？"* | `jvm-oom-analysis.md`（堆 dump + MAT 支配树） |
| *"从 Spring Boot 2.7 迁移到 3"* | `sb-migration-2-to-3.md`（6 大破坏性变更清单） |

`SKILL.md` 的 `description` 字段枚举了大量触发关键词（`@RestController`、`@SpringBootTest`、`OOM`、`GC`、`N+1`、`MyBatis-Plus` 等），所以即使你没明说"Java"，技能也能可靠触发。

## 🎨 代码风格基线

本技能里所有示例都遵循统一约定，保证生成的代码风格一致：

| 方面 | 约定 |
|------|------|
| **依赖注入** | 构造器注入，通过 `final` 字段 + `@RequiredArgsConstructor`（绝不字段 `@Autowired`） |
| **日志** | Lombok `@Slf4j` + SLF4J（绝不 `System.out.println`） |
| **DTO** | Java `record`（不可变，无需 Lombok） |
| **实体** | Lombok `@Data`（可变，配合基于 id 的 `equals`/`hashCode` —— 见 `cr-equals-hashcode.md`） |
| **持久层** | **MyBatis-Plus** 为默认（国内主流）；JPA 作为可选参考 |
| **Spring Boot** | 3.x（`jakarta.*`、Java 17+）；2.x 差异见 `sb-migration-2-to-3.md` |
| **构建工具** | Maven |

## 📑 规则索引

<details>
<summary><b>🌱 Spring Boot 开发（9 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `sb-dependency-injection.md` | HIGH | 构造器注入、Lombok 白名单、Bean 生命周期 |
| `sb-project-structure.md` | HIGH | 按特性分包的分层结构 |
| `sb-config-profiles.md` | MEDIUM | application.yml、profile、`spring.config.import` |
| `sb-mybatis-plus.md` ⭐ | HIGH | BaseMapper/IService、LambdaQueryWrapper、分页、逻辑删除 |
| `sb-jpa-repository.md` | MEDIUM | N+1、@Transactional、懒加载、Hibernate 6 UUID |
| `sb-exception-handling.md` | HIGH | @RestControllerAdvice、RFC 7807 ProblemDetail |
| `sb-rest-client.md` | MEDIUM | RestClient vs RestTemplate（已弃用）vs WebClient |
| `sb-actuator-health.md` | MEDIUM | Actuator、Micrometer、分布式链路追踪 |
| `sb-migration-2-to-3.md` ⭐ | HIGH | 2.x ↔ 3.x 迁移（6 大破坏性变更） |

</details>

<details>
<summary><b>🔍 Java 代码审查（6 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `cr-concurrency.md` | HIGH | synchronized、锁、竞态条件、原子类、虚拟线程 |
| `cr-resource-leak.md` | HIGH | try-with-resources、流、连接、锁 |
| `cr-null-safety.md` | HIGH | Optional 用法、@Nullable、NPE 防御 |
| `cr-equals-hashcode.md` | MEDIUM | equals/hashCode 契约、Record、实体相等性 |
| `cr-stream-pitfalls.md` | MEDIUM | 并行流、流复用、共享可变状态 |
| `cr-anti-patterns.md` | MEDIUM | 魔法值、异常吞噬、日志滥用 |

</details>

<details>
<summary><b>🧪 Java 测试（6 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `test-layering.md` | HIGH | 单元/切片/集成测试金字塔 |
| `test-junit5.md` | HIGH | JUnit 5 生命周期、参数化测试、扩展 |
| `test-mockito.md` | HIGH | 桩件/验证、参数匹配器、静态 mock |
| `test-testcontainers.md` ⭐ | HIGH | @ServiceConnection、真实 DB 边界、容器复用 |
| `test-spring-boot-test.md` | HIGH | @WebMvcTest / @DataJpaTest / @SpringBootTest 切片 |
| `test-coverage-assertj.md` | MEDIUM | AssertJ 流式断言、JaCoCo 覆盖率 |

</details>

<details>
<summary><b>🔥 JVM 排障（5 条规则）</b></summary>

| 规则 | 影响 | 覆盖内容 |
|------|------|----------|
| `jvm-gc-tuning.md` | HIGH | G1 / ZGC / Parallel 选型、堆内存设置 |
| `jvm-oom-analysis.md` | HIGH | OOM 自动 dump、MAT 支配树、泄漏模式 |
| `jvm-thread-dump.md` | HIGH | 死锁检测、阻塞线程、线程泄漏 |
| `jvm-cpu-high.md` | HIGH | top -Hp + jstack + async-profiler 火焰图 |
| `jvm-gc-logs.md` | MEDIUM | -Xlog:gc* 解读、GCEasy |

</details>

## 📦 Git 命令行入门

给协作者的简易命令行教程，涵盖全局设置、创建新仓库、推送已有仓库。

### 全局设置（每台电脑一次）

```bash
git config --global user.name "Zander"
git config --global user.email "zd@zdking.com"
```

### 创建新仓库

```bash
mkdir java-development-skill
cd java-development-skill
git init
touch README.md
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/zander-zyx/java-development-skill.git
git push -u origin main
```

### 推送已有仓库

```bash
cd existing_git_repo
git remote add origin https://github.com/zander-zyx/java-development-skill.git
git branch -M main
git push -u origin main
```

### 多远程镜像推送（GitHub / cnb.cool / Gitee）

本仓库在三个平台同步镜像。要一次推送到全部三个平台：

```bash
# 一次性：添加额外的远程
git remote add cnb   https://cnb.cool/zdking/java-development-skill
git remote add gitee https://gitee.com/zdking_project/java-development-skill.git

# 创建一个聚合推送地址，自动扇出到三个平台
git remote set-url --add --push origin https://github.com/zander-zyx/java-development-skill.git
git remote set-url --add --push origin https://cnb.cool/zdking/java-development-skill
git remote set-url --add --push origin https://gitee.com/zdking_project/java-development-skill.git

# 现在 `git push` 会同时推送到三个平台
git push
```

或者分别推送各远程：

```bash
git push origin main   # GitHub
git push cnb    main   # cnb.cool
git push gitee  main   # Gitee
```

> **注意**：如果你重写了历史（比如 amend、rebase），需要用 `git push --force-with-lease` 更新每个远程。

## 🤝 如何贡献

这是个人技能包，但欢迎 PR：

1. **错别字 / 表述优化** —— 直接提 PR，无需讨论。
2. **新增规则** —— 先开 issue 讨论范围。遵循现有文件结构：frontmatter（`title` / `impact` / `tags` / `description`）+ 章节（`Why it matters` / `Correct` / `Incorrect` / `Context`）。
3. **框架行为更新** —— Java/Spring 演进很快。如果某条规则在当前版本已过时，提 PR 修正并在 `Context` 里注明版本。

技能编写时对齐的版本见 `metadata.json`。

## 📜 许可证

MIT —— 见 [LICENSE](LICENSE)。可自由使用、修改、分发。注明出处感谢但不强制。

---

**编写时间**：2026 年 7 月 · **目标版本**：Spring Boot 3.x + Java 17/21 · **默认持久层**：MyBatis-Plus
