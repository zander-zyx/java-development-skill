# Java Development Agent Skill

[![Java](https://img.shields.io/badge/Java-8--21%2B-blue.svg)](https://dev.java/)
[![Rules](https://img.shields.io/badge/rules-34-success.svg)](#规则索引)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- TOTAL_RULES: 34 -->
<!-- CORE_RULES: 4 -->
<!-- BUILD_RULES: 2 -->
<!-- SPRING_BOOT_RULES: 10 -->
<!-- CODE_REVIEW_RULES: 7 -->
<!-- TESTING_RULES: 6 -->
<!-- JVM_RULES: 5 -->

一个面向 AI 编程 Agent 的 Java/JVM 通用 skill。它适用于普通 Java、类库、CLI 工具、Maven/Gradle 构建、Spring Boot 服务、测试、代码审查、安全审查、迁移和 JVM 线上排障。

## 这个 skill 优先保证什么

1. **现有项目优先** —— 保留当前 Java 版本、构建工具、框架、日志、持久层、测试栈和代码风格，除非用户明确要求改变。
2. **先通用 Java，后框架专项** —— 先识别项目，再决定是否应用 Spring Boot、MyBatis-Plus、JPA、Lombok、Testcontainers 等规则。
3. **小改动、可验证** —— 优先最小安全改动，并汇报实际执行的编译/测试/诊断命令。
4. **按需加载上下文** —— `SKILL.md` 只路由到当前任务需要的规则，不一次性加载全部文档。
5. **生产安全默认值** —— 不暗中转换技术栈，不做无关大重构，不顺手升级依赖/Java 版本，不编造业务规则。

## Agent 行为契约

启用该 skill 时，Agent 应该：

- 只查看与任务相关的文件：构建描述、源码布局、受影响代码、附近测试和框架配置。
- 保留 Maven/Gradle/其他构建工具；不能因为某条规则存在就引入另一个构建系统。
- 只有项目已经使用 Lombok 时才使用 Lombok。
- 把 Spring Boot 当作可选专项，而不是所有 Java 任务的默认前提。
- 保留现有持久层选择：MyBatis、MyBatis-Plus、JPA/Hibernate、JDBC、jOOQ 或项目自定义栈。
- 非平凡改动必须汇报：修改原因、影响范围、已验证、未验证、如何验证。

## 仓库结构

```text
java-development/
├── SKILL.md                  # 路由与运行时指令
├── core/                     # 通用 Java 工作流、API、异常、现代化
├── build-tools/              # Maven 与 Gradle 构建规则
├── spring-boot/              # 可选 Spring Boot 专项规则
├── code-review/              # Java 审查与安全检查
├── testing/                  # 单测、切片、集成、Mockito、Testcontainers
├── jvm/                      # OOM、CPU、线程 dump、GC 调优/日志分析
├── assets/                   # 可选模板
├── examples/                 # Prompt 示例
├── scripts/validate-skill.py # 仓库本地校验脚本
├── agents/openai.yaml        # OpenAI/Codex UI 元数据
└── metadata.json             # Skill 元数据
```

## 代码风格基线

这些是默认值，不是强制迁移：

| 方向 | 基线 |
|---|---|
| 项目技术栈 | 现有项目约定优先 |
| Java 版本 | 保留当前 target；只有项目支持或用户要求时才使用新语法 |
| 构建工具 | 保留 Maven、Gradle、Bazel、Ant 或仓库自定义构建方式 |
| API 设计 | 除非明确要求破坏性变更，否则保持 public API 的源码/二进制/序列化兼容 |
| DI | DI 框架中优先构造器注入；非 Lombok 项目写显式构造器 |
| 日志 | 使用现有日志门面；优先 SLF4J 兼容；生产代码避免 `System.out.println` |
| DTO/值对象 | 只有 Java 版本和框架都支持时才优先使用 `record` |
| 异常 | 保留 cause，尊重 interrupt，在系统边界映射失败 |
| 安全 | 避免注入、密钥泄漏、不安全反序列化、弱加密、SSRF、只靠客户端鉴权 |
| Spring Boot | 可选框架域；未知的现代示例使用 Spring Boot 3.x / `jakarta.*` / Java 17+ |
| 持久层 | 保留已有选择；MyBatis-Plus 只作为“新建中国式 Spring Boot 服务且未选型”时的可选默认 |

## 规则索引

### Core Java（4）

| 文件 | 影响 | 用途 |
|---|---|---|
| `core/java-general-development.md` | HIGH | 识别任意 Java 项目并选择框架中立默认策略 |
| `core/java-api-design.md` | HIGH | Public API 设计、兼容性、DTO、泛型、类库契约 |
| `core/java-exception-handling.md` | HIGH | 异常、重试、中断、日志边界、失败映射 |
| `core/java-version-modernization.md` | HIGH | Java 8/11/17/21 升级、语法现代化、toolchain、运行时检查 |

### Build tools（2）

| 文件 | 影响 | 用途 |
|---|---|---|
| `build-tools/build-maven-dependencies.md` | HIGH | Maven `pom.xml`、BOM、dependency management、scope、插件、Java release |
| `build-tools/build-gradle-dependencies.md` | HIGH | Gradle DSL、wrapper、version catalog、platform、toolchain、dependency insight |

### Spring Boot（10）

| 文件 | 影响 | 用途 |
|---|---|---|
| `spring-boot/sb-dependency-injection.md` | HIGH | Bean、DI、构造器注入、Lombok 策略 |
| `spring-boot/sb-project-structure.md` | MEDIUM | 包结构与 controller/service/repository 边界 |
| `spring-boot/sb-config-profiles.md` | HIGH | 配置、profile、密钥、config import |
| `spring-boot/sb-mybatis-plus.md` | HIGH | MyBatis/MyBatis-Plus mapper/service/query 模式 |
| `spring-boot/sb-jpa-repository.md` | HIGH | JPA/Hibernate repository、N+1、懒加载、实体身份 |
| `spring-boot/sb-exception-handling.md` | HIGH | REST 错误、参数校验错误、`ProblemDetail` |
| `spring-boot/sb-rest-client.md` | MEDIUM | `RestClient`、`WebClient`、`RestTemplate` 选择 |
| `spring-boot/sb-actuator-health.md` | MEDIUM | Actuator、健康检查、探针、指标 |
| `spring-boot/sb-migration-2-to-3.md` | HIGH | Spring Boot 2.x 到 3.x 迁移 |
| `spring-boot/sb-migration-3-to-4.md` | HIGH | Spring Boot 3.x 到 4.x 迁移规划 |

### Code review（7）

| 文件 | 影响 | 用途 |
|---|---|---|
| `code-review/cr-anti-patterns.md` | MEDIUM | 通用 Java 坏味道：魔法值、吞异常、日志滥用、可变 static |
| `code-review/cr-concurrency.md` | HIGH | 线程安全、锁、`ThreadLocal`、事务代理风险 |
| `code-review/cr-resource-leak.md` | HIGH | Closeable、JDBC、锁、线程池、泄漏风险 |
| `code-review/cr-null-safety.md` | HIGH | NPE 防护、nullable 契约、`Optional` 陷阱 |
| `code-review/cr-equals-hashcode.md` | HIGH | 相等性、哈希、实体身份、集合行为 |
| `code-review/cr-stream-pitfalls.md` | MEDIUM | Stream API、parallel stream、lambda 副作用 |
| `code-review/cr-security.md` | HIGH | 注入、密钥、加密、不安全反序列化、SSRF、鉴权漏洞 |

### Testing（6）

| 文件 | 影响 | 用途 |
|---|---|---|
| `testing/test-layering.md` | HIGH | 单元测试、切片测试、集成测试策略 |
| `testing/test-junit5.md` | HIGH | JUnit 5 生命周期、参数化测试、确定性测试 |
| `testing/test-mockito.md` | HIGH | Mockito mock、spy、static mock、验证边界 |
| `testing/test-testcontainers.md` | HIGH | 使用 Testcontainers 测真实 DB/Redis/Kafka |
| `testing/test-spring-boot-test.md` | HIGH | Spring Boot 测试切片与 `@SpringBootTest` |
| `testing/test-coverage-assertj.md` | MEDIUM | AssertJ 风格与 JaCoCo 覆盖率策略 |

### JVM troubleshooting（5）

| 文件 | 影响 | 用途 |
|---|---|---|
| `jvm/jvm-oom-analysis.md` | HIGH | OOM 分类、heap dump、泄漏分析 |
| `jvm/jvm-cpu-high.md` | HIGH | 高 CPU 诊断、热点线程、profiling |
| `jvm/jvm-thread-dump.md` | HIGH | 死锁、卡死、线程泄漏、线程池饥饿 |
| `jvm/jvm-gc-tuning.md` | HIGH | GC 暂停、堆大小、收集器选择 |
| `jvm/jvm-gc-logs.md` | MEDIUM | GC 日志解读与证据采集 |

## 校验

发布前运行：

```powershell
python scripts/validate-skill.py

$venv = Join-Path $env:TEMP 'skill-validate-venv'
if (!(Test-Path $venv)) { python -m venv $venv }
& (Join-Path $venv 'Scripts\python.exe') -m pip install -q PyYAML
& (Join-Path $venv 'Scripts\python.exe') 'C:/Users/zd/.codex/skills/.system/skill-creator/scripts/quick_validate.py' 'D:/Java_project/ai_project/skills/java-development'

git diff --check
```

## Assets

- `assets/pom-spring-boot-3.xml`：Spring Boot 3.x Maven 基线。
- `assets/pom-spring-boot-2.xml`：Spring Boot 2.x Maven 基线。
- `assets/controller-service-test.java`：Controller + service + test 骨架。
- `assets/application.yml.template`：多环境配置模板。

## License

MIT。
