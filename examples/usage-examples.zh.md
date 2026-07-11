# 使用示例

安装 skill 后可以直接粘贴这些 prompt。关键行为是：Agent 先识别 Java 项目类型，再只加载匹配的规则文件。

**中文** | [English](./usage-examples.md)

## 示例 1 —— 普通 Java / 类库代码

**Prompt**

> 重构这个 Java 工具类，但保持 Java 11 兼容，并且不要破坏 public API。

**Skill 行为**

1. 加载 `core/java-general-development.md`。
2. 先确认 Java target，再决定能不能使用新语法。
3. 不假设项目使用 Spring、Lombok 或其他框架。
4. 汇报最小编译/测试命令。

## 示例 2 —— Maven 或 Gradle 构建改动

**Prompt**

> 给这个项目加 AWS SDK 依赖，并确保依赖版本仍由统一位置管理。

**Skill 行为**

- Maven 项目：加载 `build-tools/build-maven-dependencies.md`，修改真正拥有版本的 parent/BOM/property。
- Gradle 项目：加载 `build-tools/build-gradle-dependencies.md`，尊重 version catalog、platform、convention plugin。
- 不会把 Maven 项目改成 Gradle，也不会把 Gradle 项目改成 Maven。

## 示例 3 —— Spring Boot 功能

**Prompt**

> 新增一个 OrderService 接口，保存订单，并统一返回参数校验错误。

**Skill 行为**

1. 只在项目确实是 Spring Boot 时加载对应规则，例如 `spring-boot/sb-dependency-injection.md` 或 `spring-boot/sb-exception-handling.md`。
2. 使用构造器注入。
3. 只有项目已使用 Lombok 时才用 Lombok。
4. 保留现有持久层选择：MyBatis、MyBatis-Plus、JPA 或其他方案。

## 示例 4 —— 代码审查

**Prompt**

> 审查这个方法的线程安全：
>
> ```java
> private Map<Long, Order> cache = new HashMap<>();
> public Order get(Long id) {
>     return cache.computeIfAbsent(id, this::load);
> }
> ```

**Skill 行为**

1. 加载 `code-review/cr-concurrency.md`。
2. 识别并发访问下共享可变 `HashMap` 的风险。
3. 建议 `ConcurrentHashMap`；如果需要淘汰策略，则建议 Caffeine 等有界缓存。

## 示例 5 —— JVM 线上问题

**Prompt**

> 生产环境 CPU 很高，请求延迟尖刺。我们有 thread dump 和 GC 日志。

**Skill 行为**

1. 先加载 `jvm/jvm-cpu-high.md`。
2. 因为已有证据，再补充 `jvm/jvm-thread-dump.md` 和 `jvm/jvm-gc-logs.md`。
3. 区分数据采集、诊断、临时止血和验证。

## 触发关键词

Java/JVM 术语、Maven/Gradle 文件、Spring Boot 注解、MyBatis/JPA/Hibernate、JUnit/Mockito/Testcontainers、NPE/线程安全/equals/hashCode/security/密钥/注入等代码审查词，API 兼容性词，Java 升级词，以及 OOM/GC/thread dump/deadlock/high CPU 等 JVM 排障词都可以触发该 skill。
