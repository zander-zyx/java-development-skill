---
title: General Java Development Workflow
impact: HIGH
impactDescription: Framework-first changes can break non-Spring Java projects, hide build constraints, or introduce unnecessary dependencies
tags: java, workflow, architecture, code-style, compatibility
description: Classify any Java project before editing, then preserve its runtime, build tool, framework choices, and verification path
---

## General Java Development Workflow

Use this before non-trivial Java changes, especially when the project is not obviously Spring Boot.

### Why it matters

- Java projects vary widely: CLI tools, libraries, servlet apps, Spring Boot services, Android modules, batch jobs, plugins, and legacy monoliths need different defaults.
- build-tools/runtime choices are contracts. Changing Java level, build tool, framework, logging, or persistence without evidence can break CI and deployment.
- A useful Java agent should improve the current project, not convert it to the agent's favorite stack.

### First classify the project

Before editing, inspect only what is needed:

1. **Runtime**: library, CLI, server app, batch job, test fixture, plugin, or Android.
2. **Java level**: `release`/`sourceCompatibility`, toolchain, CI image, container base image.
3. **Build tool**: Maven, Gradle, Bazel, Ant, IDE-only, or mixed repo. Do not introduce a different tool unless asked.
4. **Frameworks**: Spring, Jakarta EE, Quarkus, Micronaut, Vert.x, plain Java, Android, or none.
5. **Test stack**: JUnit 5/4, TestNG, Mockito, AssertJ, Spring Test, Testcontainers.
6. **Project conventions**: package layout, nullability annotations, logging style, Lombok usage, formatting, error handling.

### Correct default behavior

- Follow existing conventions unless they are clearly unsafe or the user asks for a new standard.
- Use the smallest change that solves the request; avoid broad refactors disguised as cleanup.
- Keep public API compatibility for libraries unless a breaking change is explicitly requested.
- Prefer constructor injection in DI frameworks; in non-DI Java, prefer explicit constructors and immutable collaborators.
- Use SLF4J or the existing logging facade in production code. Do not add `System.out.println` outside quick diagnostics or CLI output paths.
- Prefer `java.time` over legacy date/time APIs; preserve timezone semantics when changing time code.
- Prefer immutable DTO/value objects (`record` on Java 16+, final classes otherwise) when frameworks allow it.
- Keep exceptions actionable: preserve causes, avoid swallowing interrupts, and do not convert every failure to `RuntimeException` without context.

### When NOT to apply a default

- Do not add Spring Boot, Lombok, MyBatis-Plus, JPA, MapStruct, or Testcontainers just because this skill contains rules for them.
- Do not change Java 8/11 code to Java 17+ syntax unless the project already targets that runtime or the user requests modernization.
- Do not reformat whole files unless formatting is the actual task or the repository enforces it.
- Do not invent business validation rules. Ask when behavior is ambiguous.

### Verification

Pick the narrowest command that proves the change:

```bash
# Maven
mvn -q test
mvn -q -pl module -am test

# Gradle
./gradlew test
./gradlew :module:test

# Plain javac smoke check when no build exists
javac path/to/File.java
```

If verification cannot run, report the exact command attempted and the blocker.

### Context

- Cross-ref Maven changes in `build-tools/build-maven-dependencies.md`.
- Cross-ref Gradle changes in `build-tools/build-gradle-dependencies.md`.
- Cross-ref testing strategy in `testing/test-layering.md`.
- Cross-ref general review risks in `code-review/cr-anti-patterns.md`.
