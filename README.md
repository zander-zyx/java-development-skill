# Java Development Skill

[![Java](https://img.shields.io/badge/Java-17%2F21-orange.svg)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![MyBatis-Plus](https://img.shields.io/badge/MyBatis--Plus-3.5%2B-red.svg)](https://baomidou.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Rules](https://img.shields.io/badge/rules-26-success.svg)](#rule-index)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-7c3aed.svg)](#-install)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-compatible-412991.svg)](#-install)
[![OpenCode](https://img.shields.io/badge/OpenCode-compatible-ff7f0e.svg)](#-install)

**English** | [中文](./README_zh.md)

> A unified **AI Agent Skill** for Java + Spring Boot engineering — development conventions, code review, testing, and JVM troubleshooting. Designed for ZCode / Claude Code / any agent that supports the SKILL.md spec.

---

## 📖 What is this

A knowledge base that turns an AI coding agent into a **senior Java/Spring Boot engineer**. Instead of relying on the model's general Java knowledge, this skill injects curated, opinionated best practices — the kind a staff engineer would enforce in code review.

The skill is organized around **4 real-world engineering scenarios** and uses **progressive disclosure**:

- `SKILL.md` (router) is always in the agent's context — a lightweight decision tree + index.
- Individual rule files are loaded **on demand**, only when the task matches. This keeps every turn lean while the full knowledge base is 26 deep-dive rules.

This mirrors how a human engineer works: you don't re-read all of "Effective Java" every time you write a method — you look up the specific rule when it applies.

## ✨ Highlights

- **🎯 China-ecosystem first** — MyBatis-Plus is the default persistence layer (with JPA as an optional reference), matching the dominant stack in Chinese Spring Boot projects.
- **🏗 4 domains, 26 rules** — Spring Boot dev, Java code review, Java testing, JVM troubleshooting.
- **📐 Opinionated code style** — constructor injection + Lombok essentials (`@RequiredArgsConstructor` / `@Slf4j` / `@Data`), consistent across every example.
- **🔄 Version-aware** — defaults to Spring Boot 3.x (`jakarta.*`, Java 17+), with a dedicated migration guide covering all 6 breaking changes between 2.x and 3.x.
- **📋 Copy-ready templates** — Maven poms (SB2/SB3), controller-service-test skeleton, multi-environment `application.yml`.
- **🔍 Reviewer-friendly** — every code-review rule includes a checklist you can run mentally (or have the agent run) over any code.

## 📂 Project Structure

```
java-development-skill/
├── SKILL.md                # Router: decision tree + rule index (always loaded)
├── README.md               # This file (English)
├── README_zh.md            # Chinese edition
├── metadata.json           # Version metadata
├── LICENSE                 # MIT
├── install.sh              # Cross-tool one-click installer
│
├── spring-boot/            # 🌱 Domain A — Spring Boot Development (9 rules)
│   ├── sb-dependency-injection.md      Constructor injection + Lombok strategy
│   ├── sb-project-structure.md         Package-by-feature layering
│   ├── sb-config-profiles.md           application.yml + profiles + secrets
│   ├── sb-mybatis-plus.md       ⭐    BaseMapper/IService, pagination, logical delete (DEFAULT)
│   ├── sb-jpa-repository.md           JPA: N+1, @Transactional, Hibernate 6 UUID (optional)
│   ├── sb-exception-handling.md       @RestControllerAdvice + RFC 7807 ProblemDetail
│   ├── sb-rest-client.md              RestClient (new) vs RestTemplate (deprecated)
│   ├── sb-actuator-health.md          Actuator + Micrometer + tracing
│   └── sb-migration-2-to-3.md  ⭐    SB 2.x ↔ 3.x migration (6 key differences)
│
├── code-review/            # 🔍 Domain B — Java Code Review (6 rules)
│   ├── cr-concurrency.md              synchronized, locks, race conditions
│   ├── cr-resource-leak.md            try-with-resources, connections
│   ├── cr-null-safety.md              Optional, @Nullable, NPE defense
│   ├── cr-equals-hashcode.md          equals/hashCode contract, records
│   ├── cr-stream-pitfalls.md          parallel stream, reuse, mutation
│   └── cr-anti-patterns.md            magic values, swallowed exceptions, logging
│
├── testing/                # 🧪 Domain C — Java Testing (6 rules)
│   ├── test-layering.md               Unit / slice / integration pyramid
│   ├── test-junit5.md                 JUnit 5 lifecycle, parameterized, extensions
│   ├── test-mockito.md                stubbing, verification, spy, static mock
│   ├── test-testcontainers.md  ⭐    @ServiceConnection, real DB boundaries
│   ├── test-spring-boot-test.md       @WebMvcTest / @DataJpaTest / @SpringBootTest
│   └── test-coverage-assertj.md       AssertJ fluent assertions + JaCoCo
│
├── jvm/                    # 🔥 Domain D — JVM Troubleshooting (5 rules)
│   ├── jvm-gc-tuning.md               G1 / ZGC / Parallel selection + tuning
│   ├── jvm-oom-analysis.md            Heap dump + MAT dominator tree
│   ├── jvm-thread-dump.md             Deadlock detection, blocked threads
│   ├── jvm-cpu-high.md                top -Hp + jstack + async-profiler
│   └── jvm-gc-logs.md                 -Xlog:gc* interpretation
│
└── assets/                 # 📋 Copy-ready templates
    ├── pom-spring-boot-3.xml           SB3 pom (Java 17, jakarta, MyBatis-Plus)
    ├── pom-spring-boot-2.xml           SB2 pom (javax, legacy maintenance)
    ├── controller-service-test.java    Controller + Service + Mapper + Test skeleton
    └── application.yml.template        Multi-environment config (dev/prod profiles)

examples/                  # 💡 See it in action
    ├── usage-examples.md              Real prompts + what the skill produces (EN)
    └── usage-examples.zh.md           中文版
```

⭐ = highest-impact rules, read these first.

## 🚀 Install

This skill works across **four AI coding tools**. The `SKILL.md` format follows the emerging [agentskills.io](https://agentskills.io) standard — the same content loads in all of them. Each tool just looks in its own directory.

### One-click installer (recommended)

```bash
git clone https://github.com/zander-zyx/java-development-skill.git
cd java-development-skill
./install.sh
```

The installer detects which tools you have installed (Claude Code, Codex, OpenCode, ZCode) and symlinks the skill into each one's discovery directory. Options:

- `./install.sh --force` — overwrite an existing install
- `./install.sh --uninstall` — remove from all tools

### Manual install per tool

Each tool discovers skills in a different folder under `$HOME`:

| Tool | Skill path | Install command |
|------|-----------|-----------------|
| **Claude Code** | `~/.claude/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.claude/skills/java-development` |
| **OpenAI Codex** | `~/.codex/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.codex/skills/java-development` |
| **OpenCode** | `~/.opencode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.opencode/skills/java-development` |
| **ZCode** | `~/.zcode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.zcode/skills/java-development` |

> **Tip:** if a Git host is slow from your region, swap the URL for a mirror:
> - Gitee: `https://gitee.com/zdking_project/java-development-skill.git`
> - cnb.cool: `https://cnb.cool/zdking/java-development-skill`

### Project-level install (this repo only)

Want the skill active only inside one Java project? Clone into the project's local tool directory:

```bash
# inside your Java project, pick your tool:
git clone https://github.com/zander-zyx/java-development-skill.git .claude/skills/java-development
# or: .codex/skills/, .zcode/skills/, .opencode/skills/
```

### Just read the rules

The `*.md` files are plain Markdown — read them directly as a refresher, or copy individual rules into your team wiki. No tool required.

### Verify it works

After installing, restart your tool session and ask any Java / Spring Boot question. The skill auto-triggers from the `description` keywords (`@RestController`, `MyBatis-Plus`, `OOM`, `@SpringBootTest`, etc.) — you don't need to say "Java" explicitly. See [`examples/usage-examples.md`](examples/usage-examples.md) (or [中文版](examples/usage-examples.zh.md)) for real prompts and what the skill produces.

## 💡 Usage Examples

Once installed, your agent picks the right rule automatically based on context. You don't need to memorize file names.

| You say... | Skill loads... |
|-----------|----------------|
| *"Write a JPA repository for Order, watch out for N+1"* | `sb-jpa-repository.md` (N+1 → JOIN FETCH / EntityGraph) |
| *"My MyBatis-Plus pagination returns all rows"* | `sb-mybatis-plus.md` (forgot `PaginationInnerInterceptor`) |
| *"Review this class for thread safety"* | `cr-concurrency.md` + `cr-resource-leak.md` |
| *"Set up Testcontainers with MySQL"* | `test-testcontainers.md` (`@ServiceConnection`) |
| *"Prod is OOMing, how do I find the leak?"* | `jvm-oom-analysis.md` (heap dump + MAT dominator tree) |
| *"Migrating from Spring Boot 2.7 to 3"* | `sb-migration-2-to-3.md` (6 breaking changes checklist) |

The `SKILL.md` `description` frontmatter enumerates trigger keywords (`@RestController`, `@SpringBootTest`, `OOM`, `GC`, `N+1`, `MyBatis-Plus`, etc.) so the skill triggers reliably even when you don't say "Java" explicitly.

## 🎨 Code Style Baseline

Every example in this skill follows the same conventions, so generated code is consistent:

| Aspect | Convention |
|--------|-----------|
| **Dependency injection** | Constructor injection via `final` fields + `@RequiredArgsConstructor` (never field `@Autowired`) |
| **Logging** | Lombok `@Slf4j` + SLF4J (never `System.out.println`) |
| **DTOs** | Java `record` (immutable, no Lombok needed) |
| **Entities** | Lombok `@Data` (mutable, with id-based `equals`/`hashCode` — see `cr-equals-hashcode.md`) |
| **Persistence** | **MyBatis-Plus** by default (China mainstream); JPA as optional reference |
| **Spring Boot** | 3.x (`jakarta.*`, Java 17+); 2.x differences in `sb-migration-2-to-3.md` |
| **Build** | Maven |

## 📑 Rule Index

<details>
<summary><b>🌱 Spring Boot Development (9 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `sb-dependency-injection.md` | HIGH | Constructor injection, Lombok allowlist, Bean lifecycle |
| `sb-project-structure.md` | HIGH | Package-by-feature layering |
| `sb-config-profiles.md` | MEDIUM | application.yml, profiles, `spring.config.import` |
| `sb-mybatis-plus.md` ⭐ | HIGH | BaseMapper/IService, LambdaQueryWrapper, pagination, logical delete |
| `sb-jpa-repository.md` | MEDIUM | N+1, @Transactional, lazy loading, Hibernate 6 UUID |
| `sb-exception-handling.md` | HIGH | @RestControllerAdvice, RFC 7807 ProblemDetail |
| `sb-rest-client.md` | MEDIUM | RestClient vs RestTemplate (deprecated) vs WebClient |
| `sb-actuator-health.md` | MEDIUM | Actuator, Micrometer, distributed tracing |
| `sb-migration-2-to-3.md` ⭐ | HIGH | 2.x ↔ 3.x migration (6 breaking changes) |

</details>

<details>
<summary><b>🔍 Java Code Review (6 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `cr-concurrency.md` | HIGH | synchronized, locks, race conditions, atomic classes, virtual threads |
| `cr-resource-leak.md` | HIGH | try-with-resources, streams, connections, locks |
| `cr-null-safety.md` | HIGH | Optional usage, @Nullable, NPE defense |
| `cr-equals-hashcode.md` | MEDIUM | equals/hashCode contract, records, entity equality |
| `cr-stream-pitfalls.md` | MEDIUM | parallel stream, reuse, shared mutation |
| `cr-anti-patterns.md` | MEDIUM | magic values, swallowed exceptions, logging abuse |

</details>

<details>
<summary><b>🧪 Java Testing (6 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `test-layering.md` | HIGH | Unit / slice / integration test pyramid |
| `test-junit5.md` | HIGH | JUnit 5 lifecycle, parameterized tests, extensions |
| `test-mockito.md` | HIGH | Stub/spy/verify, argument matchers, static mocking |
| `test-testcontainers.md` ⭐ | HIGH | @ServiceConnection, real DB boundaries, container reuse |
| `test-spring-boot-test.md` | HIGH | @WebMvcTest / @DataJpaTest / @SpringBootTest slices |
| `test-coverage-assertj.md` | MEDIUM | AssertJ fluent assertions, JaCoCo coverage |

</details>

<details>
<summary><b>🔥 JVM Troubleshooting (5 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `jvm-gc-tuning.md` | HIGH | G1 / ZGC / Parallel selection, heap sizing |
| `jvm-oom-analysis.md` | HIGH | Heap dump on OOM, MAT dominator tree, leak patterns |
| `jvm-thread-dump.md` | HIGH | Deadlock detection, blocked threads, thread leaks |
| `jvm-cpu-high.md` | HIGH | top -Hp + jstack + async-profiler flame graphs |
| `jvm-gc-logs.md` | MEDIUM | -Xlog:gc* interpretation, GCEasy |

</details>

## 📦 Git Quick Start

A minimal command-line primer for collaborators. Covers global setup, creating a new repo, and pushing an existing repo.

### Global setup (once per machine)

```bash
git config --global user.name "Zander"
git config --global user.email "zd@zdking.com"
```

### Create a new repository

```bash
mkdir java-development-skill
cd java-development-skill
git init
touch README.md
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/zander-zyx/java-development-skill.git
git push -u origin main
```

### Push an existing repository

```bash
cd existing_git_repo
git remote add origin https://github.com/zander-zyx/java-development-skill.git
git branch -M main
git push -u origin main
```

### Mirror to multiple remotes (GitHub / cnb.cool / Gitee)

This repo is mirrored across three hosts. To push to all of them in one command:

```bash
# one-time: add the extra remotes
git remote add cnb   https://cnb.cool/zdking/java-development-skill
git remote add gitee https://gitee.com/zdking_project/java-development-skill.git

# create a single push URL that fans out to all three
git remote set-url --add --push origin https://github.com/zander-zyx/java-development-skill.git
git remote set-url --add --push origin https://cnb.cool/zdking/java-development-skill
git remote set-url --add --push origin https://gitee.com/zdking_project/java-development-skill.git

# now `git push` hits all three at once
git push
```

Or push remotes individually:

```bash
git push origin main   # GitHub
git push cnb    main   # cnb.cool
git push gitee  main   # Gitee
```

> **Note**: if you rewrite history (e.g. amend, rebase), use `git push --force-with-lease` on each remote to update.

## 🤝 How to Contribute

This is a personal skill but PRs are welcome:

1. **Typo / clarification** — direct PR, no discussion needed.
2. **New rule** — open an issue first to discuss scope. Follow the existing file structure: frontmatter (`title` / `impact` / `tags` / `description`) + sections (`Why it matters` / `Correct` / `Incorrect` / `Context`).
3. **Updated framework behavior** — Java/Spring evolves fast. If a rule is outdated for the current version, PR the fix and note the version in `Context`.

See `metadata.json` for the version this skill was authored against.

## 📜 License

MIT — see [LICENSE](LICENSE). Free to use, modify, distribute. Attribution appreciated but not required.

---

**Authored**: July 2026 · **Target**: Spring Boot 3.x + Java 17/21 · **Persistence default**: MyBatis-Plus
