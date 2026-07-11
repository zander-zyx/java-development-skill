---
title: Gradle Dependency and Build Hygiene
impact: HIGH
impactDescription: Unsafe Gradle plugin, dependency, wrapper, or Java-toolchain changes can break every module and CI task that shares the build
tags: gradle, build.gradle, kotlin-dsl, dependencies, plugins, toolchain
description: Safely edit Gradle builds by preserving wrapper versions, plugin management, dependency constraints, module boundaries, and verification evidence
---

## Gradle Dependency and Build Hygiene

Use this when editing `build.gradle`, `build.gradle.kts`, `settings.gradle`, plugin versions, dependency versions, Java toolchains, or Gradle wrapper files.

### Why it matters

- Gradle builds often centralize versions in catalogs, convention plugins, or parent scripts; editing the nearest file can bypass the real source of truth.
- Wrapper, plugin, and Java-toolchain changes affect all modules and CI.
- Dependency conflicts may compile but fail under tests or at runtime.

### First classify the build

1. **DSL**: Groovy (`build.gradle`) or Kotlin (`build.gradle.kts`). Keep the existing DSL.
2. **Modules**: inspect `settings.gradle*` for `include(...)` and composite builds.
3. **Version source**: version catalog (`gradle/libs.versions.toml`), platform/BOM, convention plugin, or inline versions.
4. **Java level**: `java.toolchain`, `sourceCompatibility`, target compatibility, CI/runtime image.
5. **Framework plugin**: plain `java`/`java-library`, Spring Boot, Shadow, Android, Kotlin, Micronaut, Quarkus, etc.

### Correct

Prefer Java toolchains when the project already supports modern Gradle:

```kotlin
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}
```

Use the project's central version mechanism. Examples:

```kotlin
// Version catalog preferred when present
implementation(libs.guava)
testImplementation(libs.junit.jupiter)
```

```groovy
// BOM/platform preferred when already used
implementation platform("org.springframework.boot:spring-boot-dependencies:${springBootVersion}")
implementation "org.springframework.boot:spring-boot-starter-web"
```

### Rules

- Do not edit `gradle-wrapper.properties` unless the task requires a Gradle upgrade; wrapper changes need full CI verification.
- Do not mix Maven files into a Gradle-only project or Gradle files into a Maven-only project.
- Do not duplicate dependency versions inline when `libs.versions.toml`, `dependencyManagement`, or a platform already owns them.
- Keep `api` vs `implementation` intentional in `java-library` projects; `api` leaks transitive dependencies to consumers.
- For Spring Boot 4 builds, verify the Spring Boot Gradle plugin's documented compatibility before upgrading the plugin or wrapper; Spring Boot 4.1 documents Gradle 8.x (8.14+) or 9.x support.
- Keep annotation processors (`lombok`, `mapstruct-processor`) in `annotationProcessor` / `testAnnotationProcessor` or the existing convention.

### Evidence commands

```bash
./gradlew test
./gradlew :module:test
./gradlew dependencies --configuration runtimeClasspath
./gradlew dependencyInsight --dependency group-or-artifact --configuration runtimeClasspath
./gradlew javaToolchains
```

For Windows-only repos, also consider:

```powershell
.\gradlew.bat test
```

### When NOT to use

- Do not rewrite Groovy DSL to Kotlin DSL, or vice versa, unless requested.
- Do not collapse multi-module builds into a single module for convenience.
- Do not upgrade plugins, Gradle, or Java level as a side effect of adding an unrelated dependency.

### Context

- Cross-ref general project classification in `core/java-general-development.md`.
- Cross-ref Maven-specific rules in `build-tools/build-maven-dependencies.md`.
- Cross-ref Spring Boot migration rules only when the project actually uses Spring Boot. Official Spring Boot Gradle plugin docs: https://docs.spring.io/spring-boot/gradle-plugin/index.html.
