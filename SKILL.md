---
name: java-development
description: Java + Spring Boot development, code review, testing, and JVM troubleshooting. Covers Spring Boot (controllers, services, repositories, config, exceptions, REST clients, Security/Web), persistence (MyBatis-Plus default; Spring Data JPA/Hibernate optional), testing (JUnit 5, Mockito, AssertJ, Testcontainers), code review (concurrency, resource leaks, NPE/Optional, equals/hashCode, Stream pitfalls), and JVM (GC, OOM, thread dump, deadlock, high CPU). Trigger on Java, JVM, Spring Boot, MyBatis(-Plus), JPA, Maven pom.xml, Bean/DI, Lombok, jakarta.*/javax.*, or any Java write/test/review request.
metadata:
  author: personal
  version: "1.0.0"
---

# Java Development

A unified skill for Java + Spring Boot engineering: development conventions, code review, testing, and JVM troubleshooting. Organized into 4 domains with progressive disclosure — this file is the router; detailed rules live in subdirectories and are read on demand.

## Code Style Baseline (applies to ALL examples in this skill)

All code in this skill follows these defaults. Read `spring-boot/sb-dependency-injection.md` for the full rationale.

- **Dependency injection**: constructor injection via `final` fields + Lombok `@RequiredArgsConstructor`. Never `@Autowired` on fields.
- **Logging**: Lombok `@Slf4j` + SLF4J. Never `System.out.println` in production code.
- **Data classes**: prefer Java `record` for immutable DTOs; use Lombok `@Data` only for mutable entities/JPA `@Entity`.
- **Null safety**: use `Optional` as return type; annotate fields/params with `@Nullable`/`@NonNull` (JSR-305 or Spring's).
- **Spring Boot version**: examples default to **Spring Boot 3.x** (`jakarta.*`, Java 17+). For 2.x differences see `spring-boot/sb-migration-2-to-3.md`.
- **Build tool**: Maven (Gradle equivalents noted where they differ).
- **Persistence layer**: **MyBatis-Plus is the default** (matches the China mainstream). JPA/Hibernate covered as an optional reference for OSS / foreign-company contexts. See `spring-boot/sb-mybatis-plus.md` for the default.

## When to Apply

Reference the appropriate domain when the user is:

- **A. Building Spring Boot apps** — controllers, services, repositories, config, JPA entities, exception handling, REST clients, actuator
- **B. Reviewing Java code** — concurrency bugs, resource leaks, NPE risks, equals/hashCode contracts, Stream misuse
- **C. Writing Java tests** — JUnit 5, Mockito, AssertJ, Testcontainers, Spring Boot Test slices
- **D. Troubleshooting the JVM** — GC tuning, OOM analysis, thread dumps, high CPU, performance profiling

## Workflow / Decision Tree

When a task comes in, first identify which domain it belongs to. A task may span multiple domains — read the relevant rule file from each.

1. **Is it about writing/configuring Spring Boot code?** → Domain A. Read the specific rule below (e.g. writing a JPA entity → `sb-jpa-repository.md`; setting up an exception handler → `sb-exception-handling.md`).

2. **Is the user asking to review/audit existing Java code, or did they paste code to check?** → Domain B. Read `cr-concurrency.md`, `cr-resource-leak.md`, `cr-null-safety.md` as relevant. Cross-cutting review → start with `cr-anti-patterns.md`.

3. **Is it about writing tests or test setup?** → Domain C. Test strategy first → `test-layering.md`; specific framework → the matching file. Testcontainers questions → `test-testcontainers.md`.

4. **Is it a production/runtime problem (OOM, slow, CPU spike, dead lock)?** → Domain D. Start from the symptom: OOM → `jvm-oom-analysis.md`; CPU high → `jvm-cpu-high.md`; hung/deadlock → `jvm-thread-dump.md`; GC pauses → `jvm-gc-tuning.md` + `jvm-gc-logs.md`.

If unclear which domain, inspect the context (mentions of `@RestController` → A; `synchronized`/`ExecutorService` → B; `@Test`/`Mockito` → C; `jstack`/`-Xmx`/GC → D).

## Rule Index

### A. Spring Boot Development (`spring-boot/`)

| File | Covers | Priority |
|------|--------|----------|
| `sb-dependency-injection.md` | Constructor injection, Lombok strategy, Bean lifecycle | HIGH |
| `sb-project-structure.md` | Layered structure: controller/service/repository/dto | HIGH |
| `sb-config-profiles.md` | application.yml, profiles, spring.config.import | MEDIUM |
| `sb-mybatis-plus.md` | BaseMapper/IService, LambdaQueryWrapper, pagination, logical delete (default) | HIGH |
| `sb-jpa-repository.md` | JPA: N+1, @Transactional, lazy loading, Hibernate 6 UUID (optional) | MEDIUM |
| `sb-exception-handling.md` | @RestControllerAdvice, global exception handling | HIGH |
| `sb-rest-client.md` | RestClient (new) vs RestTemplate (deprecated) vs WebClient | MEDIUM |
| `sb-actuator-health.md` | actuator, health checks, metrics | MEDIUM |
| `sb-migration-2-to-3.md` | Spring Boot 2.x ↔ 3.x migration (6 key differences) | HIGH |

### B. Java Code Review (`code-review/`)

| File | Covers | Priority |
|------|--------|----------|
| `cr-concurrency.md` | synchronized, locks, race conditions, atomic classes | HIGH |
| `cr-resource-leak.md` | try-with-resources, streams, connections | HIGH |
| `cr-null-safety.md` | Optional usage, NPE defense, @Nullable | HIGH |
| `cr-equals-hashcode.md` | equals/hashCode contract, records | MEDIUM |
| `cr-stream-pitfalls.md` | Stream parallel, short-circuit, reuse misuse | MEDIUM |
| `cr-anti-patterns.md` | magic values, swallowed exceptions, logging abuse | MEDIUM |

### C. Java Testing (`testing/`)

| File | Covers | Priority |
|------|--------|----------|
| `test-layering.md` | Unit / slice / integration test layering strategy | HIGH |
| `test-junit5.md` | JUnit 5 lifecycle, parameterized, extensions | HIGH |
| `test-mockito.md` | Mockito stub/spy/verify, static mocking | HIGH |
| `test-testcontainers.md` | @ServiceConnection, container reuse | HIGH |
| `test-spring-boot-test.md` | @SpringBootTest / @WebMvcTest / @DataJpaTest | HIGH |
| `test-coverage-assertj.md` | AssertJ chaining, JaCoCo coverage | MEDIUM |

### D. JVM Troubleshooting (`jvm/`)

| File | Covers | Priority |
|------|--------|----------|
| `jvm-gc-tuning.md` | GC selection (G1/ZGC/Parallel) + tuning | HIGH |
| `jvm-oom-analysis.md` | OOM: heap dump + MAT analysis flow | HIGH |
| `jvm-thread-dump.md` | Thread dump + deadlock detection | HIGH |
| `jvm-cpu-high.md` | High CPU: top -Hp + jstack + flame graph | HIGH |
| `jvm-gc-logs.md` | GC log interpretation (-Xlog:gc*) | MEDIUM |

## How to Use

Read the specific rule file before producing code or analysis:

```
spring-boot/sb-jpa-repository.md
testing/test-testcontainers.md
jvm/jvm-oom-analysis.md
```

Each rule file contains:
- **Why it matters** — the concrete harm of getting it wrong
- **Correct** — example with explanation
- **Incorrect / When NOT to use** — anti-pattern OR guidance on when the rule doesn't apply
- **Context** — version differences, edge cases, references

## Asset Templates

Copy-ready scaffolding under `assets/`:

- `pom-spring-boot-3.xml` — Spring Boot 3.x Maven pom (Java 17, jakarta)
- `pom-spring-boot-2.xml` — Spring Boot 2.x Maven pom (javax)
- `controller-service-test.java` — Controller + Service + Test three-layer skeleton
- `application.yml.template` — multi-environment config template

## Notes

- **Version currency**: The Java/Spring ecosystem moves fast. Check `metadata.json` for the version date; rules reference Spring Boot 3.x + Java 17/21 as of authoring. The `sb-migration-2-to-3.md` file tracks the current state of versions (incl. 4.x).
- **Self-contained**: Examples assume no specific project structure beyond standard Maven layout, so the skill is portable.
