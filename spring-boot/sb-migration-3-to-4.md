---
title: Spring Boot 3.x to 4.x Migration
impact: HIGH
impactDescription: Spring Boot 4 changes framework, Jakarta EE, servlet-container, and dependency baselines; direct upgrades can fail at compile time or startup
tags: migration, spring-boot-3, spring-boot-4, spring-framework-7, jakarta-ee-11, servlet-6.1
description: Migrate Spring Boot 3.x applications to 4.x conservatively by staging through the latest 3.5.x line, checking Java/build baselines, Jakarta EE 11, and removed support
---

## Spring Boot 3.x to 4.x Migration

Use this only for projects that already run Spring Boot 3.x and need a 4.x migration plan or code changes.

### Why it matters

Spring Boot 4 is not a routine patch upgrade. It aligns with Spring Framework 7 and newer Jakarta EE / Servlet baselines, so dependencies, servlet containers, starters, and framework integrations must be checked together.

### Migration order

1. **Get current on 3.5.x first**: upgrade within Spring Boot 3.x, remove deprecations, and make tests green before changing to 4.x.
2. **Check runtime and build baselines**: verify Java runtime, CI image, Maven/Gradle plugin versions, and container images against the official Spring Boot 4 requirements.
3. **Check dependencies**: every third-party starter, servlet container, persistence library, tracing library, and internal starter must declare Spring Boot 4 / Spring Framework 7 compatibility.
4. **Handle removed support early**: if the app uses a removed or no-longer-managed integration, replace it before the main version bump.
5. **Upgrade one service/module at a time** with a rollback path and dependency tree diff.

### Known high-risk checks

- **Java**: Spring Boot 4.1 requires Java 17+; confirm CI and deployment runtime, not only local `JAVA_HOME`.
- **Spring Framework**: Spring Boot 4.1 requires Spring Framework 7.0.x+; remove Spring 6 deprecations before upgrading.
- **Build tools**: Spring Boot 4.1 documents Maven 3.6.3+ and Gradle 8.x (8.14+) or 9.x support.
- **Servlet containers**: Spring Boot 4.1 documents Tomcat 11 / Jetty 12.1 and Servlet 6.1+ deployment. Undertow is not in the supported embedded container list, so treat Undertow usage as a migration blocker until verified.
- **Jakarta baseline**: validate Jakarta EE / Servlet API compatibility for filters, custom starters, generated code, app servers, and third-party libraries.
- **HTTP clients**: prefer `RestClient` for new synchronous clients; do not mass-rewrite stable `RestTemplate` usage unless migration evidence requires it.
- **Third-party starters**: every security, persistence, tracing, cloud, and internal starter must declare Spring Boot 4 / Spring Framework 7 compatibility.

### Evidence commands

```bash
# Maven
mvn -q test
mvn -q dependency:tree -Dverbose

# Gradle
./gradlew test
./gradlew dependencies --configuration runtimeClasspath
./gradlew dependencyInsight --dependency spring-boot --configuration runtimeClasspath
```

Also run the app's startup smoke test and at least one integration test path that touches web, data, security, and observability.

### When NOT to migrate

- Do not migrate directly from Spring Boot 2.x to 4.x. Move to 3.5.x first and use `spring-boot/sb-migration-2-to-3.md`.
- Do not upgrade shared libraries/starter BOMs without checking all downstream services.
- Do not mix Spring Boot 4 starters into a Spring Boot 3 application.

### Context

- Use official Spring Boot migration guides and system requirements as the source of truth for exact removals and supported versions. Relevant official docs: https://docs.spring.io/spring-boot/system-requirements.html and https://docs.spring.io/spring-boot/gradle-plugin/index.html.
- Cross-ref build changes in `build-tools/build-maven-dependencies.md` or `build-tools/build-gradle-dependencies.md`.
- Cross-ref HTTP client choices in `spring-boot/sb-rest-client.md`.
- Cross-ref Spring tests in `testing/test-spring-boot-test.md`.
