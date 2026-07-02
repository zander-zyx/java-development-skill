---
title: Spring Boot 2.x to 3.x Migration
impact: HIGH
impactDescription: Migration breaks apps at 6 well-known points; knowing them turns a multi-day debug into a checklist
tags: migration, spring-boot-2, spring-boot-3, jakarta, hibernate, native, sleuth
description: Spring Boot 2.x→3.x has 6 key breaking changes — javax→jakarta, JDK 17, Hibernate 6, trailing-slash, HttpClient 5, observability
alwaysApply: true
---

## Spring Boot 2.x to 3.x Migration

Spring Boot 3.0 (Nov 2022) was the biggest breaking release since 1.x. Migration breaks at 6 predictable points. Work through them as a checklist.

### Version timeline (as of July 2026)

| Line | Status |
|------|--------|
| **2.7.18** | Last 2.x release (2023-11). OSS support **ended**; commercial support extended to ~Jun 2029. |
| **3.x** | Active. 3.4.x OSS ended (3.4.13 final); 3.5.x is the current active line. |
| **4.1.0** | Current latest stable (Jun 2026), based on Spring Framework 7.0.8. |

If you're on 2.7, migrate to 3.x before considering 4.x. Spring Framework 7.0 (in SB4) deprecates `RestTemplate` — plan to move sync HTTP calls to `RestClient` (see `sb-rest-client.md`).

### The 6 breaking changes

#### 1. `javax.*` → `jakarta.*` (highest impact)

Spring Boot 3 moved to Jakarta EE 9+. Every import of `javax.servlet`, `javax.persistence`, `javax.validation`, `javax.annotation` changes namespace:

```java
// 2.x
import javax.servlet.http.HttpServletRequest;
import javax.persistence.Entity;
import javax.validation.constraints.NotBlank;

// 3.x
import jakarta.servlet.http.HttpServletRequest;
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotBlank;
```

**Mechanics**: this is a project-wide find/replace. Use the **OpenRewrite recipe** `org.openrewrite.java.migrate.jakarta.JavaxMigrationToJakarta` to automate it safely — it handles edge cases (e.g. `javax.annotation.Nullable` vs `jakarta.annotation.Nullable` differences) that a naive sed misses.

**Third-party jars**: any dependency still on `javax.*` (older versions of some libs) won't be Jakarta-compatible. Upgrade them or find alternatives.

#### 2. JDK 17 minimum

SB 2.x supports Java 8+. SB 3.x requires **Java 17+** (3.2+ recommends 21). Update your build toolchain:

```xml
<properties>
    <java.version>17</java.version>
    <maven.compiler.release>17</maven.compiler.release>
</properties>
```

Java 8→17 itself has removals (`SecurityManager` restrictions, `sun.*` APIs, strong encapsulation of JDK internals). Add `--add-opens` flags for libraries that reflect into JDK internals (Lombok, older bytecodegen).

#### 3. Hibernate 5 → 6 (JPA pitfalls)

Hibernate 6 changes three behaviors you'll trip on:

**a. `@GeneratedValue(strategy = GenerationType.AUTO)` now resolves to IDENTITY** (was SEQUENCE/TABLE). If you relied on a sequence, switch to explicit:

```java
// explicit — survives the AUTO semantic change
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "order_seq")
@SequenceGenerator(name = "order_seq", sequenceName = "order_seq", allocationSize = 1)
private Long id;
```

**b. UUID column type changes**. Hibernate 6 maps `UUID` to `uuid` (PostgreSQL) or `binary(16)`/`varchar(36)` differently than 5. Existing schemas may need a column-type override. Verify with `ddl-auto=validate` on staging.

**c. `@Type` API refactored**. The Hibernate 5 custom-type annotation is replaced by `@Type(Class<? extends UserimeType>)` in Hibernate 6, and many old `@Type` values no longer compile. Migrate to `@Convert(converter = ...)` or the new `@JavaType`/`@JdbcType`.

Bonus: Hibernate 6 / JPA 3.1 added `GenerationType.UUID` for native UUID generation (see `sb-jpa-repository.md`).

#### 4. Trailing-slash matching flipped (most common regression)

Spring MVC in Spring 6 changed the default for **trailing-slash matching** from `true` to `false`:

- `/api/orders` no longer matches `/api/orders/` → **404** for any client that appends a slash.

This is the single most-reported SB3 regression. Two fixes:

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void configurePathMatch(PathMatchConfigurer configurer) {
        configurer.setUseTrailingSlashMatch(true);   // restore 2.x behavior
    }
}
```

Or fix the clients to not append slashes. Note: `setUseTrailingSlashMatch` is **deprecated and slated for removal in Spring Framework 7.0** — the long-term answer is consistent client paths, not re-enabling the legacy behavior.

#### 5. Apache HttpClient 4 → 5

Spring Framework 6 dropped support for Apache HttpClient 4; SB 3.1 removed its dependency management. If you used HttpClient 4 as a transport:

```xml
<!-- ❌ no longer managed -->
<!-- <artifactId>httpclient</artifactId> -->

<!-- ✅ HttpClient 5 -->
<dependency>
    <groupId>org.apache.httpcomponents.client5</groupId>
    <artifactId>httpclient5</artifactId>
</dependency>
```

The HttpClient 5 API differs substantially (different package names, builder pattern). If you only used it as the underlying transport for `RestTemplate`/`WebClient`, you can switch to JDK `HttpClient` instead — simpler and no extra dep.

#### 6. Observability: Sleuth → Micrometer Tracing

Spring Cloud **Sleuth is deprecated** (SB2 only). SB3 ships **Micrometer Tracing + Observation API** built in.

```xml
<!-- ❌ SB2 only -->
<!-- spring-cloud-starter-sleuth -->

<!-- ✅ SB3 -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>otlp-exporter</artifactId>
</dependency>
```

Note: **default trace formats differ** between Sleuth and Micrometer Tracing — propagation headers changed, so a rolling migration can lose traces at the boundary. Cut over a service fully, don't half-migrate.

### Also: `spring.factories` → AutoConfiguration.imports

If you wrote a custom starter, auto-config registration moved:

- **2.x**: `META-INF/spring.factories` with `org.springframework.boot.autoconfigure.EnableAutoConfiguration=...`
- **3.x**: `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (one FQCN per line)

The old mechanism still works in 3.x but is deprecated and on a removal track.

### Recommended migration order

1. **On 2.7 first** — upgrade any older 2.x to 2.7.18, fix deprecation warnings. The `spring-boot-properties-migrator` dependency logs renamed properties.
2. **Bump JDK to 17** while still on 2.7 — isolates Java issues from Spring issues.
3. **Run OpenRewrite** for the `javax`→`jakarta` sweep.
4. **Bump to 3.x**, fix Hibernate 6 + trailing-slash regressions.
5. **Cutover observability** to Micrometer Tracing.
6. **Validate** with `ddl-auto=validate`, full test suite, and a staging load test.

```xml
<!-- useful during 2.7 phase: logs renamed property keys -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-properties-migrator</artifactId>
    <scope>runtime</scope>
</dependency>
```

### Context

- **Native Image**: SB3 makes GraalVM AOT a first-class feature (`spring-boot-maven-plugin` `native` goal). SB2's `spring-native` experiment is dead. Not a migration blocker, but a reason to move.
- **Cross-ref**: HttpClient/RestClient selection in `sb-rest-client.md`; Hibernate 6 UUID/entity equality in `sb-jpa-repository.md`; MP starter artifact id (`mybatis-plus-spring-boot3-starter` vs `mybatis-plus-boot-starter`) in `sb-mybatis-plus.md`.
- **Source**: [Spring Boot 3.0 Migration Guide (wiki)](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide).
