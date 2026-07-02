# Java Development Skill

A unified skill for Java + Spring Boot engineering, organized into 4 domains:

- **Spring Boot Development** — controllers, services, repositories, config, JPA, exceptions, REST clients, actuator
- **Java Code Review** — concurrency, resource leaks, NPE/Optional, equals/hashCode, Stream pitfalls
- **Java Testing** — JUnit 5, Mockito, AssertJ, Testcontainers, Spring Boot Test slices
- **JVM Troubleshooting** — GC tuning, OOM analysis, thread dumps, high CPU

## Code Style Baseline

All examples in this skill follow:

- Constructor injection via `final` fields + Lombok `@RequiredArgsConstructor` (no field `@Autowired`)
- Lombok `@Slf4j` for logging (no `System.out.println`)
- Java `record` for immutable DTOs; Lombok `@Data` only for JPA `@Entity`
- Spring Boot 3.x (`jakarta.*`) as default; 2.x differences covered in `sb-migration-2-to-3.md`
- Maven as build tool

## How it's organized

```
SKILL.md                  ← router: decision tree + rule index (always loaded)
spring-boot/              ← 8 rule files (loaded on demand)
code-review/              ← 6 rule files
testing/                  ← 6 rule files
jvm/                      ← 5 rule files
assets/                   ← copy-ready templates (pom, skeleton, config)
```

The SKILL.md stays in context; each rule file is read only when relevant. This keeps the skill rich without bloating every turn.

## For AI agents

To force-load this skill on a specific prompt, the SKILL.md frontmatter `description` enumerates trigger keywords (@RestController, @SpringBootTest, OOM, GC, N+1, etc.). When authoring Java code, the model should consult the matching rule file before writing.

## Version

See `metadata.json`. Authored July 2026 against Spring Boot 3.x + Java 17/21.
