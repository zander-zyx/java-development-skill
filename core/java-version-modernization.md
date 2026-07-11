---
title: Java Version Modernization
impact: HIGH
impactDescription: Java upgrades can break compilation, runtime flags, reflection, dependencies, containers, and CI even when source changes look small
tags: java, migration, modernization, java-8, java-11, java-17, java-21, toolchain
description: Modernize Java versions safely by separating language changes from runtime/build/dependency upgrades and preserving compatibility requirements
---

## Java Version Modernization

Use this when upgrading Java 8/11/17/21, introducing newer language features, changing compiler release, or modernizing old Java idioms.

### Why it matters

Java modernization is not just syntax cleanup. Runtime images, bytecode target, reflection access, removed JDK modules, TLS defaults, GC flags, annotation processors, and dependencies can all fail independently.

### Upgrade order

1. **Identify the real target**: build `release`, CI JDK, runtime container, production JVM, and downstream consumers.
2. **Upgrade build/toolchain first** without source refactors.
3. **Make tests green** on the new JDK.
4. **Upgrade incompatible dependencies** with evidence.
5. **Then modernize syntax** in small, reviewable changes.

### Rules

- Use `--release` / Maven `maven.compiler.release` / Gradle toolchains when possible.
- Do not use `var`, `record`, text blocks, switch expressions, or pattern matching unless the target Java version supports them.
- For Java 8 to 11+, check removed Java EE/JAXB modules and old JVM flags.
- For Java 8/11 to 17+, check strong encapsulation and reflective access warnings/errors.
- For Java 17 to 21+, check virtual thread usage carefully; do not mix with blocking code assumptions blindly.
- Update annotation processors such as Lombok and MapStruct before blaming the compiler.
- Preserve public API bytecode compatibility for libraries unless a major-version break is accepted.

### Correct modernization examples

Use `java.time` for new date/time code:

```java
Instant now = clock.instant();
LocalDate businessDate = LocalDate.now(clock);
```

Use `record` only when target and framework support it:

```java
public record UserSummary(Long id, String name) {}
```

### When NOT to modernize

- Do not introduce new syntax into a module targeting Java 8/11.
- Do not combine a JDK upgrade with unrelated business refactors.
- Do not remove compatibility flags until staging proves dependencies no longer need them.

### Verification

```bash
java -version
mvn -q -version
mvn -q test
./gradlew javaToolchains
./gradlew test
```

Also verify the runtime image or deployment base image, not only the local compiler.

### Context

- Cross-ref Maven release config in `build-tools/build-maven-dependencies.md`.
- Cross-ref Gradle toolchains in `build-tools/build-gradle-dependencies.md`.
- Cross-ref JVM tuning after runtime changes in `jvm/jvm-gc-tuning.md`.
