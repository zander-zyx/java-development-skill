---
name: java-development
description: Use when working on Java, JVM, Spring Boot, Maven pom.xml, MyBatis or MyBatis-Plus, JPA or Hibernate, Lombok, jakarta.* or javax.*, Java tests, Java code review, or JVM runtime troubleshooting such as GC, OOM, thread dumps, deadlocks, high CPU, and performance issues.
---

# Java Development

Router skill for Java + Spring Boot work. Keep this file light: load only the matching rule files below, then answer or edit code using those rules.

## Defaults

- Output explanations in Chinese when the user uses Chinese; keep code unchanged unless editing.
- Spring Boot examples default to 3.x, `jakarta.*`, Java 17+; read `spring-boot/sb-migration-2-to-3.md` for 2.x/4.x migration questions.
- Maven is the default build tool.
- MyBatis-Plus is the default persistence layer for China-style Spring Boot projects; JPA/Hibernate is optional unless the project already uses it.
- Use constructor injection with `final` fields + Lombok `@RequiredArgsConstructor`; never field `@Autowired`.
- Use Lombok `@Slf4j` + SLF4J; never `System.out.println` in production code.
- Prefer Java `record` for immutable DTOs; use mutable classes only when frameworks require them.

## Loading Rules

Start with the smallest useful set:

- Normal feature/edit: load 1 primary rule file, plus 1 cross-cutting file only if needed.
- Broad code review: start with `code-review/cr-anti-patterns.md`, then add specific risk files.
- Test work: load `testing/test-layering.md` first, then the framework-specific test file.
- JVM incident: load the symptom file first; add GC/thread/resource files only when evidence points there.
- Do not load README files or `examples/` unless the user asks for usage docs.

## Route By Task

| Task signal | Read first | Add if needed |
|---|---|---|
| DI, beans, Lombok, service/controller skeleton | `spring-boot/sb-dependency-injection.md` | `spring-boot/sb-project-structure.md` |
| Package layout, controller/service/repository boundaries | `spring-boot/sb-project-structure.md` | `spring-boot/sb-exception-handling.md` |
| `application.yml`, profiles, secrets, config import | `spring-boot/sb-config-profiles.md` | `spring-boot/sb-actuator-health.md` |
| MyBatis, MyBatis-Plus, mapper, wrapper, pagination | `spring-boot/sb-mybatis-plus.md` | `code-review/cr-equals-hashcode.md` |
| JPA, Hibernate, N+1, lazy loading, transactions | `spring-boot/sb-jpa-repository.md` | `code-review/cr-equals-hashcode.md` |
| REST API error handling, validation errors | `spring-boot/sb-exception-handling.md` | `code-review/cr-null-safety.md` |
| HTTP clients, RestClient, WebClient, RestTemplate | `spring-boot/sb-rest-client.md` | `spring-boot/sb-config-profiles.md` |
| Actuator, health, metrics, probes | `spring-boot/sb-actuator-health.md` | `jvm/jvm-gc-logs.md` |
| Spring Boot 2->3, 3->4, javax/jakarta | `spring-boot/sb-migration-2-to-3.md` | `spring-boot/sb-rest-client.md` |
| Java code review, general smell scan | `code-review/cr-anti-patterns.md` | specific review files below |
| Thread safety, locks, `ThreadLocal`, transactions proxy | `code-review/cr-concurrency.md` | `code-review/cr-resource-leak.md` |
| Closeable, JDBC, locks, thread pools, leaks | `code-review/cr-resource-leak.md` | `jvm/jvm-oom-analysis.md` |
| NPE, `Optional`, nullable contracts | `code-review/cr-null-safety.md` | `spring-boot/sb-exception-handling.md` |
| `equals`, `hashCode`, entity identity | `code-review/cr-equals-hashcode.md` | persistence rule in use |
| Stream API, parallel stream, lambda side effects | `code-review/cr-stream-pitfalls.md` | `code-review/cr-concurrency.md` |
| Test strategy, unit/slice/integration choice | `testing/test-layering.md` | one test framework file |
| JUnit 5 lifecycle, parameterized tests | `testing/test-junit5.md` | `testing/test-coverage-assertj.md` |
| Mockito mocks, spies, static mocks | `testing/test-mockito.md` | `testing/test-layering.md` |
| Testcontainers, real DB/Redis/Kafka | `testing/test-testcontainers.md` | `testing/test-spring-boot-test.md` |
| `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest` | `testing/test-spring-boot-test.md` | `testing/test-testcontainers.md` |
| AssertJ, JaCoCo, coverage floor | `testing/test-coverage-assertj.md` | framework-specific test file |
| OOM, heap dump, memory leak | `jvm/jvm-oom-analysis.md` | `code-review/cr-resource-leak.md` |
| High CPU, hot thread, profiling | `jvm/jvm-cpu-high.md` | `jvm/jvm-thread-dump.md` |
| Hang, deadlock, thread leak | `jvm/jvm-thread-dump.md` | `code-review/cr-concurrency.md` |
| GC pause, heap sizing, collector choice | `jvm/jvm-gc-tuning.md` | `jvm/jvm-gc-logs.md` |
| GC log interpretation | `jvm/jvm-gc-logs.md` | `jvm/jvm-gc-tuning.md` |

## Assets

- `assets/pom-spring-boot-3.xml`: Spring Boot 3.x Maven baseline.
- `assets/pom-spring-boot-2.xml`: Spring Boot 2.x Maven baseline.
- `assets/controller-service-test.java`: Controller + service + test skeleton.
- `assets/application.yml.template`: multi-environment config template.
