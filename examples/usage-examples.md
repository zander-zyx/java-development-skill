# Usage Examples

Prompts you can paste after installing the skill. The important behavior is that the agent first identifies the Java project type, then loads only the matching rule files.

**English** | [中文](./usage-examples.zh.md)

## Example 1 — Plain Java / library code

**Prompt**

> Refactor this Java utility class, but keep Java 11 compatibility and public API stable.

**Skill behavior**

1. Loads `core/java-general-development.md`.
2. Checks Java target before using newer syntax.
3. Avoids Spring/Lombok/framework assumptions.
4. Reports the minimal compile/test command.

## Example 2 — Maven or Gradle build change

**Prompt**

> Add the AWS SDK dependency to this project and make sure dependency versions stay managed.

**Skill behavior**

- Maven project: loads `build-tools/build-maven-dependencies.md` and edits the owning parent/BOM/property.
- Gradle project: loads `build-tools/build-gradle-dependencies.md` and respects version catalogs/platforms/convention plugins.
- It does not convert one build tool to another.

## Example 3 — Spring Boot feature

**Prompt**

> Add an OrderService endpoint that saves an order and returns validation errors consistently.

**Skill behavior**

1. Loads the relevant Spring Boot rule, such as `spring-boot/sb-dependency-injection.md` or `spring-boot/sb-exception-handling.md`.
2. Uses constructor injection.
3. Uses Lombok only if the project already uses Lombok.
4. Preserves the existing persistence choice: MyBatis, MyBatis-Plus, JPA, or something else.

## Example 4 — Code review

**Prompt**

> Review this method for thread safety:
>
> ```java
> private Map<Long, Order> cache = new HashMap<>();
> public Order get(Long id) {
>     return cache.computeIfAbsent(id, this::load);
> }
> ```

**Skill behavior**

1. Loads `code-review/cr-concurrency.md`.
2. Flags shared mutable `HashMap` under concurrent access.
3. Suggests `ConcurrentHashMap` or a bounded cache such as Caffeine when eviction is required.

## Example 5 — JVM incident

**Prompt**

> Production has high CPU and request latency spikes. We have thread dumps and GC logs.

**Skill behavior**

1. Starts with `jvm/jvm-cpu-high.md`.
2. Adds `jvm/jvm-thread-dump.md` and `jvm/jvm-gc-logs.md` only because evidence exists.
3. Separates data collection, diagnosis, mitigation, and verification.

## Trigger keywords

The skill can trigger from Java/JVM terms, Maven/Gradle files, Spring Boot annotations, MyBatis/JPA/Hibernate terms, JUnit/Mockito/Testcontainers, code-review terms such as NPE/thread-safety/equals/hashCode/security/secrets/injection, API compatibility terms, Java upgrade terms, and JVM incident terms such as OOM/GC/thread dump/deadlock/high CPU.
