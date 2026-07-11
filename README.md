# Java Development Agent Skill

[![Java](https://img.shields.io/badge/Java-8--21%2B-blue.svg)](https://dev.java/)
[![Rules](https://img.shields.io/badge/rules-34-success.svg)](#rule-index)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- TOTAL_RULES: 34 -->
<!-- CORE_RULES: 4 -->
<!-- BUILD_RULES: 2 -->
<!-- SPRING_BOOT_RULES: 10 -->
<!-- CODE_REVIEW_RULES: 7 -->
<!-- TESTING_RULES: 6 -->
<!-- JVM_RULES: 5 -->

A framework-neutral Java/JVM skill for AI coding agents. It is designed for everyday Java development across plain Java, libraries, CLI tools, Maven/Gradle builds, Spring Boot services, tests, code review, security review, migrations, and JVM production incidents.

## What this skill optimizes for

1. **Existing project first** — preserve the current Java version, build tool, framework, logging, persistence, tests, and style unless the user asks to change them.
2. **General Java before frameworks** — classify the project before applying Spring Boot, MyBatis-Plus, JPA, Lombok, or Testcontainers guidance.
3. **Small, verifiable changes** — prefer the smallest safe edit and report the exact compile/test/diagnostic command used.
4. **On-demand context** — `SKILL.md` routes to the smallest useful rule set instead of loading all rules.
5. **Production-safe defaults** — no hidden stack conversion, broad refactor, dependency upgrade, Java-version bump, or business-rule invention.

## Agent contract

When this skill is active, the agent should:

- Inspect only task-relevant files: build descriptor, source layout, affected code, nearby tests, and framework configuration.
- Preserve Maven/Gradle/other build tools; never add another build system just because a rule exists.
- Use Lombok only when the project already uses Lombok.
- Treat Spring Boot as an optional domain, not the default for all Java work.
- Preserve existing persistence choices: MyBatis, MyBatis-Plus, JPA/Hibernate, JDBC, jOOQ, or other project-specific stacks.
- For non-trivial work, report change reason, impact scope, verified items, unverified items, and how to verify.

## What this skill is not

- Not a Spring Boot-specific template or a starter-project generator.
- Not a style enforcer that rewrites build tools, persistence layers, Java versions, or frameworks.
- Not a replacement for repository-specific `AGENTS.md`, architecture docs, CI rules, or business requirements.

## Repository layout

```text
java-development/
├── SKILL.md                  # Router and runtime instructions
├── core/                     # General Java workflow, API, exceptions, modernization
├── build-tools/              # Maven and Gradle build hygiene
├── spring-boot/              # Optional Spring Boot-specific rules
├── code-review/              # Java review and security checks
├── testing/                  # Unit, slice, integration, Mockito, Testcontainers
├── jvm/                      # OOM, CPU, thread dump, GC tuning/log analysis
├── assets/                   # Optional templates
├── examples/                 # Prompt examples
├── scripts/validate-skill.py # Repository-local validator
├── agents/openai.yaml        # OpenAI/Codex UI metadata
└── metadata.json             # Skill metadata
```

## Code style baseline

These are defaults, not forced migrations:

| Area | Baseline |
|---|---|
| Project stack | Existing project conventions win |
| Java level | Preserve current target; use newer syntax only when supported/requested |
| Build tool | Preserve Maven, Gradle, Bazel, Ant, or repo-specific build setup |
| API design | Preserve public source/binary/serialization compatibility unless a breaking change is requested |
| DI | Constructor injection in DI frameworks; explicit constructors outside Lombok projects |
| Logging | Use the existing logging facade; prefer SLF4J-compatible logging; avoid production `System.out.println` |
| DTO/value objects | Prefer `record` only when Java version and frameworks support it |
| Exceptions | Preserve causes, respect interrupts, and map failures at system boundaries |
| Security | Avoid injected queries, leaked secrets, unsafe deserialization, weak crypto, SSRF, and client-only authorization |
| Spring Boot | Optional framework domain; unknown modern examples use Spring Boot 3.x / `jakarta.*` / Java 17+ |
| Persistence | Preserve existing choice; MyBatis-Plus is only an optional new China-style Spring Boot default when no choice exists |

## Rule index

### Core Java (4)

| File | Impact | Purpose |
|---|---|---|
| `core/java-general-development.md` | HIGH | Classify any Java project and choose framework-neutral defaults |
| `core/java-api-design.md` | HIGH | Public API design, compatibility, DTOs, generics, library contracts |
| `core/java-exception-handling.md` | HIGH | Exceptions, retries, interrupts, logging boundaries, failure mapping |
| `core/java-version-modernization.md` | HIGH | Java 8/11/17/21 upgrades, syntax modernization, toolchains, runtime checks |

### Build tools (2)

| File | Impact | Purpose |
|---|---|---|
| `build-tools/build-maven-dependencies.md` | HIGH | Maven `pom.xml`, BOMs, dependency management, scopes, plugins, Java release |
| `build-tools/build-gradle-dependencies.md` | HIGH | Gradle DSL, wrapper, version catalogs, platforms, toolchains, dependency insight |

### Spring Boot (10)

| File | Impact | Purpose |
|---|---|---|
| `spring-boot/sb-dependency-injection.md` | HIGH | Beans, DI, constructor injection, Lombok strategy |
| `spring-boot/sb-project-structure.md` | HIGH | Package layout and controller/service/repository boundaries |
| `spring-boot/sb-config-profiles.md` | MEDIUM | Config, profiles, secrets, config import |
| `spring-boot/sb-mybatis-plus.md` | HIGH | MyBatis/MyBatis-Plus mapper/service/query patterns |
| `spring-boot/sb-jpa-repository.md` | HIGH | JPA/Hibernate repositories, N+1, lazy loading, entity identity |
| `spring-boot/sb-exception-handling.md` | HIGH | REST errors, validation errors, `ProblemDetail` |
| `spring-boot/sb-rest-client.md` | MEDIUM | `RestClient`, `WebClient`, `RestTemplate` selection |
| `spring-boot/sb-actuator-health.md` | MEDIUM | Actuator, health checks, probes, metrics |
| `spring-boot/sb-migration-2-to-3.md` | HIGH | Spring Boot 2.x to 3.x migration |
| `spring-boot/sb-migration-3-to-4.md` | HIGH | Spring Boot 3.x to 4.x migration planning |

### Code review (7)

| File | Impact | Purpose |
|---|---|---|
| `code-review/cr-anti-patterns.md` | MEDIUM | General Java smell scan: magic values, swallowed exceptions, log abuse, mutable statics |
| `code-review/cr-concurrency.md` | HIGH | Thread safety, locks, `ThreadLocal`, transaction proxy risks |
| `code-review/cr-resource-leak.md` | HIGH | Closeables, JDBC, locks, thread pools, leak risks |
| `code-review/cr-null-safety.md` | HIGH | NPE prevention, nullable contracts, `Optional` pitfalls |
| `code-review/cr-equals-hashcode.md` | MEDIUM | Equality, hashing, entity identity, collection behavior |
| `code-review/cr-stream-pitfalls.md` | MEDIUM | Stream API, parallel stream, lambda side effects |
| `code-review/cr-security.md` | HIGH | Injection, secrets, crypto, unsafe deserialization, SSRF, authorization gaps |

### Testing (6)

| File | Impact | Purpose |
|---|---|---|
| `testing/test-layering.md` | HIGH | Unit, slice, integration test strategy |
| `testing/test-junit5.md` | HIGH | JUnit 5 lifecycle, parameterized tests, deterministic tests |
| `testing/test-mockito.md` | HIGH | Mockito mocks, spies, static mocks, verification boundaries |
| `testing/test-testcontainers.md` | HIGH | Real DB/Redis/Kafka tests with Testcontainers |
| `testing/test-spring-boot-test.md` | HIGH | Spring Boot test slices and `@SpringBootTest` |
| `testing/test-coverage-assertj.md` | MEDIUM | AssertJ style and JaCoCo coverage policy |

### JVM troubleshooting (5)

| File | Impact | Purpose |
|---|---|---|
| `jvm/jvm-oom-analysis.md` | HIGH | OOM classification, heap dumps, leak analysis |
| `jvm/jvm-cpu-high.md` | HIGH | High CPU diagnosis, hot threads, profiling |
| `jvm/jvm-thread-dump.md` | HIGH | Deadlocks, hangs, thread leaks, pool starvation |
| `jvm/jvm-gc-tuning.md` | HIGH | GC pauses, heap sizing, collector selection |
| `jvm/jvm-gc-logs.md` | MEDIUM | GC log interpretation and evidence collection |

## Validation

Run before publishing changes:

```powershell
python scripts/validate-skill.py

$venv = Join-Path $env:TEMP 'skill-validate-venv'
if (!(Test-Path $venv)) { python -m venv $venv }
& (Join-Path $venv 'Scripts\python.exe') -m pip install -q PyYAML
& (Join-Path $venv 'Scripts\python.exe') 'C:/Users/zd/.codex/skills/.system/skill-creator/scripts/quick_validate.py' 'D:/Java_project/ai_project/skills/java-development'

git diff --check
```

## Assets

- `assets/pom-spring-boot-3.xml`: Spring Boot 3.x Maven baseline.
- `assets/pom-spring-boot-2.xml`: Spring Boot 2.x Maven baseline.
- `assets/controller-service-test.java`: Controller + service + test skeleton.
- `assets/application.yml.template`: multi-environment config template.

## License

MIT.
