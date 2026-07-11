---
title: Maven Dependency and Build Hygiene
impact: HIGH
impactDescription: Incorrect dependency, BOM, plugin, or Java-release changes can break CI or fail at runtime across one or more modules
tags: maven, pom, dependencies, bom, plugins, java-release
description: Safely edit Maven pom.xml files by preserving project dependency management, scopes, module boundaries, and verification evidence
---

## Maven Dependency and Build Hygiene

Use this when editing `pom.xml`, dependency versions, Maven plugins, BOMs, compiler release level, annotation processors, or Maven module structure.

### Why it matters

- Dependency drift is production risk: overriding managed versions can introduce binary incompatibilities that compile but fail at runtime.
- Build files are shared contracts: parent/BOM/plugin changes affect all modules and CI, not just the file being edited.
- Transitive conflicts are subtle: duplicate logging, servlet, JSON, bytecode, or `javax`/`jakarta` APIs often appear only under integration tests.

### First classify the project

Before changing `pom.xml`, identify:

1. **Packaging**: single module vs multi-module (`<modules>`).
2. **Parent/BOM**: corporate parent, Spring Boot parent, imported BOMs, or explicit versions.
3. **Java level**: `maven.compiler.release`, `java.version`, or compiler plugin config.
4. **Dependency source**: dependencyManagement, properties, imported platform, or inline versions.
5. **Test stack**: Surefire/Failsafe, JUnit 5/4, Mockito, Testcontainers, framework test plugin.
6. **Framework line if present**: Spring Boot, Jakarta EE, Quarkus, Micronaut, plain Java, etc.

If the project already has a convention, follow it instead of applying defaults blindly.

### Correct

Prefer managed versions over scattered inline versions:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>example-bom</artifactId>
            <version>${example.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

Prefer `release` over separate `source`/`target` when the project can use it:

```xml
<properties>
    <java.version>17</java.version>
    <maven.compiler.release>${java.version}</maven.compiler.release>
</properties>
```

For Spring Boot apps, prefer the Spring Boot parent unless the project already uses a corporate parent. With a corporate parent, import `spring-boot-dependencies` in `<dependencyManagement>` instead of inventing unmanaged starter versions.

### Rules

- Do not set versions for dependencies managed by the active BOM unless there is a documented override reason.
- Put unavoidable explicit versions in `<properties>`; avoid scattered inline versions.
- Do not mix `javax.*` and `jakarta.*` APIs accidentally; align with the framework/runtime line.
- Keep annotation processors (`lombok`, `mapstruct-processor`) under `maven-compiler-plugin` when the project already uses explicit processor paths.
- Preserve `provided`, `runtime`, `test`, and optional scopes; scope changes can alter packaged artifacts.
- In multi-module projects, change the parent/module that actually owns the version, not every child POM.

### Evidence commands

```bash
mvn -q test
mvn -q -pl module -am test
mvn -q dependency:tree -Dincludes=groupId:artifactId
mvn -q dependency:tree -Dverbose
mvn -q help:effective-pom
```

When resolving conflicts, exclude at the nearest dependency that introduces the unwanted transitive dependency. Do not add broad exclusions at the parent unless the whole reactor needs them.

### When NOT to use

- Do not introduce Maven into a Gradle-only project.
- Do not upgrade Java, Maven plugins, or BOMs as a side effect unless required by the task.
- Do not replace an existing corporate parent with a framework parent without explicit approval.

### Context

- Cross-ref general project classification in `core/java-general-development.md`.
- Cross-ref Gradle-specific rules in `build-tools/build-gradle-dependencies.md`.
- Cross-ref Spring Boot migration rules only when the project actually uses Spring Boot.
