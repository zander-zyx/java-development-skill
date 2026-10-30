---
name: java-development
description: "Use when writing, refactoring, or reviewing any Java or JVM code: plain Java, libraries, CLI tools, Android Java, Maven/Gradle dependency and build governance (pom.xml, BOMs, version catalogs, toolchains), Spring Boot development and version migration (2.x to 3.x, 3.x to 4.x, javax to jakarta), MyBatis/MyBatis-Plus or JPA/Hibernate persistence, writing tests with JUnit 5, Mockito, AssertJ, and Testcontainers, API design, exception handling, security review, Java upgrades, and JVM troubleshooting such as OOM, high CPU, GC tuning, GC logs, thread dumps, deadlocks, and memory leaks. Also covers Jakarta EE, Quarkus, Micronaut, and Lombok. Not for non-JVM languages or general questions unrelated to Java code."
---

# Java Development Agent

Router skill for general Java/JVM work. Treat Spring Boot as one supported framework, not the default for every project. Load only the matching rule files below.

## Routing Protocol

Run these three steps in order before generating or modifying code.

### Step 1 — Stack Detection

Inspect the project's build descriptor(s) first and record what they prove:

- `pom.xml` vs `build.gradle(.kts)` → Maven or Gradle; preserve whichever exists.
- Java version → `maven.compiler.release` / `<java.version>` / Gradle toolchain or `sourceCompatibility`.
- Spring Boot line → parent or BOM version: 2.x, 3.x, or 4.x (drives jakarta namespace, security DSL, Actuator/Micrometer config).
- Persistence → JPA/Hibernate vs MyBatis/MyBatis-Plus vs JDBC/jOOQ (dependencies plus repository/mapper layout).
- Lombok → present and annotation processing configured, or absent.
- Logging facade → SLF4J, Log4j2, or JUL in actual use.
- Test stack → JUnit 4 vs 5, Mockito, Testcontainers, Spring Boot test slices.

Existing evidence beats this skill's defaults. If a descriptor answers a question, do not assume otherwise.

### Step 2 — Lazy Routing (Progressive Disclosure)

Classify the task, then read **only the 1–3 highest-matching rule files** from the route table. Never load every rule file for one task — it inflates the context window without improving the answer.

- Unknown/general Java task: load `core/java-general-development.md` only if classification or the default choice is unclear.
- API/exception/version work: load the specific `core/...` rule before framework rules.
- Build edits: load exactly one `build-tools/...` rule matching the detected build tool.
- Spring Boot edits: load the primary `spring-boot/...` rule only when the project actually uses Spring Boot.
- Broad code review: start with `code-review/cr-anti-patterns.md`, then add specific risk files.
- Test work: load `testing/test-layering.md` first, then the framework-specific test file.
- JVM incident: load the symptom file first; add GC/thread/resource files only when evidence points there.
- Do not load README files or `examples/` unless the user asks for usage docs.

### Step 3 — Convention Priority

The target project's existing code style, architecture, and module conventions outrank this skill's rules. When they conflict, follow the project and say so explicitly.

## Defaults

- Respond in the user's language; keep code unchanged unless editing.
- Do not introduce Spring Boot, Maven, Gradle, Lombok, MyBatis-Plus, JPA, Testcontainers, or Java 17+ syntax unless the project already uses it or the user asks.
- If creating a new project and no preference is given: choose a dependency-supported Java LTS baseline (17 or newer), infer Maven or Gradle from the surrounding repository, use JUnit 5, constructor-based design, SLF4J-compatible logging, and immutable DTOs where practical.
- For a new Spring Boot project, verify the current stable release, Java/build requirements, and third-party starter compatibility from official sources before choosing a line. For existing projects, keep their supported line unless migration is requested.
- Do not choose a persistence framework by geography or popularity. Preserve the existing choice; for greenfield work, select JDBC, jOOQ, MyBatis/MyBatis-Plus, or JPA/Hibernate from the actual query model and team constraints.
- Prefer constructor injection in DI frameworks. Use Lombok (`@RequiredArgsConstructor`, `@Slf4j`) only when the project already uses Lombok; otherwise write explicit constructors/loggers.
- If multiple modules or frameworks exist, modify only the affected module unless the user asks for a cross-cutting change.
- Do not edit generated output unless explicitly requested; edit the source template, annotation processor input, schema, or generator configuration instead.

## Work Rules

- Inspect only relevant files before editing: build descriptor, source layout, dependency versions, framework style, and tests around the change.
- Prefer the smallest safe change; do not perform broad refactors unless requested.
- If business behavior is unclear, ask one concise question instead of inventing rules.
- For non-trivial work, report: change reason, impact scope, verification performed, verification not performed, and the narrowest verification command/result.

## Route By Task

| Task signal | Read first | Add if needed |
|---|---|---|
| Unknown Java project, framework-neutral edit, library/CLI code | `core/java-general-development.md` | add matching `build-tools/...`, `testing/...`, or `code-review/...` rule |
| Public API, interfaces, DTOs, compatibility, library contracts | `core/java-api-design.md` | `code-review/cr-null-safety.md` |
| Exceptions, retries, interrupts, failure boundaries | `core/java-exception-handling.md` | `code-review/cr-resource-leak.md` |
| Java 8/11/17/21/25 upgrade, newer syntax, toolchain | `core/java-version-modernization.md` | `build-tools/build-maven-dependencies.md` or `build-tools/build-gradle-dependencies.md` |
| Maven `pom.xml`, dependencies, BOM, plugins, Java release | `build-tools/build-maven-dependencies.md` | relevant `spring-boot/...`, `testing/...`, or migration rule |
| Gradle `build.gradle(.kts)`, wrapper, version catalog, toolchain | `build-tools/build-gradle-dependencies.md` | relevant `spring-boot/...`, `testing/...`, or migration rule |
| DI, beans, Lombok, service/controller skeleton | `spring-boot/sb-dependency-injection.md` | `spring-boot/sb-project-structure.md` |
| Package layout, controller/service/repository boundaries | `spring-boot/sb-project-structure.md` | `spring-boot/sb-exception-handling.md` |
| `application.yml`, profiles, secrets, config import | `spring-boot/sb-config-profiles.md` | `spring-boot/sb-actuator-health.md` |
| MyBatis, MyBatis-Plus, mapper, wrapper, pagination | `spring-boot/sb-mybatis-plus.md` | `code-review/cr-equals-hashcode.md` |
| JPA, Hibernate, N+1, lazy loading, transactions | `spring-boot/sb-jpa-repository.md` | `code-review/cr-equals-hashcode.md` |
| REST API error handling, validation errors | `spring-boot/sb-exception-handling.md` | `code-review/cr-null-safety.md` |
| HTTP clients, RestClient, WebClient, RestTemplate | `spring-boot/sb-rest-client.md` | `spring-boot/sb-config-profiles.md` |
| Actuator, health, metrics, probes | `spring-boot/sb-actuator-health.md` | `jvm/jvm-gc-logs.md` |
| Spring Boot 2->3, `javax`/`jakarta` migration | `spring-boot/sb-migration-2-to-3.md` | `build-tools/...` plus `spring-boot/sb-rest-client.md` when HTTP clients are affected |
| Spring Boot 3->4, Framework 7/Jakarta/Servlet baseline | `spring-boot/sb-migration-3-to-4.md` | `build-tools/...`, `spring-boot/sb-rest-client.md`, and affected `testing/...` rules |
| Java code review, general smell scan | `code-review/cr-anti-patterns.md` | specific review files below |
| Security review, secrets, injection, crypto, deserialization, SSRF | `code-review/cr-security.md` | `spring-boot/sb-config-profiles.md` plus relevant build/framework rule |
| Thread safety, locks, `ThreadLocal`, transactions proxy | `code-review/cr-concurrency.md` | `code-review/cr-resource-leak.md` |
| Closeable, JDBC, locks, thread pools, leaks | `code-review/cr-resource-leak.md` | `jvm/jvm-oom-analysis.md` |
| NPE, `Optional`, nullable contracts | `code-review/cr-null-safety.md` | `core/java-exception-handling.md` or framework error rule |
| `equals`, `hashCode`, entity identity | `code-review/cr-equals-hashcode.md` | `spring-boot/sb-jpa-repository.md` or `spring-boot/sb-mybatis-plus.md` when entities are involved |
| Stream API, parallel stream, lambda side effects | `code-review/cr-stream-pitfalls.md` | `code-review/cr-concurrency.md` |
| Test strategy, unit/slice/integration choice | `testing/test-layering.md` | `testing/test-junit5.md`, `testing/test-mockito.md`, `testing/test-spring-boot-test.md`, or `testing/test-testcontainers.md` |
| JUnit 5 lifecycle, parameterized tests | `testing/test-junit5.md` | `testing/test-coverage-assertj.md` |
| Mockito mocks, spies, static mocks | `testing/test-mockito.md` | `testing/test-layering.md` |
| Testcontainers, real DB/Redis/Kafka | `testing/test-testcontainers.md` | `testing/test-spring-boot-test.md` |
| `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest` | `testing/test-spring-boot-test.md` | `testing/test-testcontainers.md` |
| AssertJ, JaCoCo, coverage floor | `testing/test-coverage-assertj.md` | affected `testing/...` framework rule |
| OOM, heap dump, memory leak | `jvm/jvm-oom-analysis.md` | `code-review/cr-resource-leak.md` |
| High CPU, hot thread, profiling | `jvm/jvm-cpu-high.md` | `jvm/jvm-thread-dump.md` |
| Hang, deadlock, thread leak | `jvm/jvm-thread-dump.md` | `code-review/cr-concurrency.md` |
| GC pause, heap sizing, collector choice | `jvm/jvm-gc-tuning.md` | `jvm/jvm-gc-logs.md` |
| GC log interpretation | `jvm/jvm-gc-logs.md` | `jvm/jvm-gc-tuning.md` |

## Assets

- `assets/pom-spring-boot-3.xml`: opt-in Spring Boot 3.x + MyBatis-Plus Maven example.
- `assets/pom-spring-boot-2.xml`: opt-in legacy Spring Boot 2.7 maintenance example.
- `assets/controller-service-test.java`: opt-in Spring Boot 3 + MyBatis-Plus skeleton; split it into real files before use.
- `assets/application.yml.template`: opt-in multi-environment Spring Boot + MyBatis-Plus config example.
