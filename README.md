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

## 📑 Table of Contents

- [📖 What is this](#-what-is-this) · [🎯 Why use a skill](#-why-use-a-skill) · [✨ Highlights](#-highlights)
- [📂 Project Structure](#-project-structure) · [🚀 Install](#-install) · [💡 How to use](#-how-to-use)
- [🛠 Troubleshooting](#-troubleshooting) · [🎨 Code Style Baseline](#-code-style-baseline) · [📑 Rule Index](#-rule-index)
- [🤝 How to Contribute](#-how-to-contribute) · [📜 License](#-license)

---

## 📖 What is this

A knowledge base that turns an AI coding agent into a **senior Java/Spring Boot engineer**. Instead of relying on the model's general Java knowledge, this skill injects curated, opinionated best practices — the kind a staff engineer would enforce in code review.

The skill is organized around **4 real-world engineering scenarios** and uses **progressive disclosure**:

- `SKILL.md` is a lightweight router loaded after the skill triggers — defaults, loading budget, and a route table.
- Individual rule files are loaded **on demand**, only when the task matches. This keeps every turn lean while the full knowledge base remains 26 deep-dive rules.

This mirrors how a human engineer works: you don't re-read all of "Effective Java" every time you write a method — you look up the specific rule when it applies.

## ✨ Highlights

- **🎯 China-ecosystem first** — MyBatis-Plus is the default persistence layer (with JPA as an optional reference), matching the dominant stack in Chinese Spring Boot projects.
- **🏗 4 domains, 26 rules** — Spring Boot dev, Java code review, Java testing, JVM troubleshooting.
- **📐 Opinionated code style** — constructor injection + Lombok essentials (`@RequiredArgsConstructor` / `@Slf4j` / `@Data`), consistent across every example.
- **🔄 Version-aware** — defaults to Spring Boot 3.x (`jakarta.*`, Java 17+), with a dedicated migration guide covering all 6 breaking changes between 2.x and 3.x.
- **📋 Copy-ready templates** — Maven poms (SB2/SB3), controller-service-test skeleton, multi-environment `application.yml`.
- **🔍 Reviewer-friendly** — every code-review rule includes a checklist you can run mentally (or have the agent run) over any code.

## 🎯 Why use a skill

Modern LLMs already "know" Java. So why install this skill? Because general knowledge is **unopinionated** and **inconsistent across turns** — the model will write field-injection today and constructor-injection tomorrow. This skill locks in **one coherent set of conventions** and surfaces the right rule at the right moment.

| Without the skill | With this skill |
|-------------------|-----------------|
| Model picks injection style by mood | Always constructor injection + `@RequiredArgsConstructor` |
| Forgets `@Transactional(rollbackFor=Exception.class)` on checked exceptions | Rule auto-applied |
| Reaches for H2 to "test" MyBatis SQL | Uses Testcontainers + real MySQL |
| Generic "check for thread safety" advice | Runs the `code-review/cr-concurrency.md` checklist item by item |
| Guesses SB 2.x vs 3.x behavior | Loads `spring-boot/sb-migration-2-to-3.md`, gets the 6 breaking changes |
| Copy-pastes stale Lombok advice (`@AllArgsConstructor`) | Restricted to the Lombok allowlist |

The skill is the difference between "an AI that can write Java" and "an AI that writes Java the way your team does".

### Requirements

- **Git** — to clone the repo
- **One of**: Claude Code, OpenAI Codex CLI, OpenCode, or ZCode installed
- **OS**: macOS, Linux, or Windows (Git Bash / WSL for the installer script)
- **No Java/JDK required to use the skill** — it's knowledge for the agent, not a runtime dependency. (Your Java project itself obviously needs a JDK.)

## 📂 Project Structure

```
java-development-skill/
├── SKILL.md                # Router: loading budget + route table (loaded after trigger)
├── README.md               # This file (English)
├── README_zh.md            # Chinese edition
├── AGENTS.md               # Always-on engineering discipline for Codex-style agents
├── metadata.json           # Version metadata
├── LICENSE                 # MIT
├── install.sh              # Cross-tool one-click installer
├── agents/openai.yaml      # Codex UI metadata
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
├── assets/                 # 📋 Copy-ready templates
│   ├── pom-spring-boot-3.xml           SB3 pom (Java 17, jakarta, MyBatis-Plus)
│   ├── pom-spring-boot-2.xml           SB2 pom (javax, legacy maintenance)
│   ├── controller-service-test.java    Controller + Service + Mapper + Test skeleton
│   └── application.yml.template        Multi-environment config (dev/prod profiles)
│
├── examples/               # 💡 See it in action
│   ├── usage-examples.md               Real prompts + what the skill produces (EN)
│   └── usage-examples.zh.md            中文版
│
├── install.sh              # 🔧 Cross-tool one-click installer
├── LICENSE                 # MIT
└── metadata.json           # Version metadata
```

⭐ = highest-impact rules, read these first.

## 🚀 Install

This skill works across **four AI coding tools**. The `SKILL.md` format follows the emerging [agentskills.io](https://agentskills.io) standard — the same content loads in all of them. Each tool just looks in its own directory.

### Prerequisites

Before installing the skill, you need **Git** and **at least one supported AI tool** already on your machine. The skill is just knowledge for the agent — it does not need Java or a JDK itself (your Java project does).

| Prerequisite | Check it's installed | How to install |
|--------------|---------------------|----------------|
| **Git** | `git --version` | [git-scm.com](https://git-scm.com/downloads) |
| **Claude Code** | `claude --version` | `npm install -g @anthropic-ai/claude-code` |
| **OpenAI Codex** | `codex --version` | [developers.openai.com/codex](https://developers.openai.com/codex) |
| **OpenCode** | `opencode --version` | [opencode.ai/docs](https://opencode.ai/docs/) |
| **ZCode** | check `~/.zcode/` exists | your ZCode distribution |

You only need **one** of the four tools. Pick whichever you already use.

### Option 1 — One-click installer (recommended)

The installer auto-detects which of the four tools you have and links the skill into each one's folder.

```bash
# 1. clone the repo
git clone https://github.com/zander-zyx/java-development-skill.git

# 2. enter it
cd java-development-skill

# 3. run the installer
./install.sh
```

**Expected output** (you'll see one line per tool you have installed):
```
✓ claude: linked → /Users/you/.claude/skills/java-development
✓ codex:  linked → /Users/you/.codex/skills/java-development
Done. The 'java-development' skill is now active in the tools above.
Restart any running tool sessions to pick it up.
```

Installer options:
- `./install.sh --force` — overwrite an existing install (re-link after a clone URL change, etc.)
- `./install.sh --uninstall` — remove the skill from all detected tools
- `./install.sh --help` — show usage

> **Slow from your region?** Clone from a mirror first, then run the same installer:
> ```bash
> git clone https://gitee.com/zdking_project/java-development-skill.git   # Gitee (China)
> # or: https://cnb.cool/zdking/java-development-skill                    # cnb.cool
> cd java-development-skill && ./install.sh
> ```

> **Windows users**: run the installer in **Git Bash** or **WSL** (not cmd.exe / PowerShell). Git Bash comes with Git for Windows. If the symlink step falls back to a copy, that's fine — re-run `git pull && ./install.sh --force` to update.

### Option 2 — Let your AI tool install it (no terminal needed)

You're already using an AI coding agent — the easiest path is to ask it to install the skill for you. Open a chat in Claude Code / Codex / OpenCode / ZCode and paste:

```
Install the java-development skill from https://github.com/zander-zyx/java-development-skill
into your skill directory, then confirm it's loaded.
```

The agent will `git clone` the repo into its own skill folder, verify the `SKILL.md` is in place, and tell you when it's done. You don't need to know the path or run any command yourself.

**What the agent does** (so you know what to expect):
1. Clones the repo into this tool's skills directory (e.g. `~/.claude/skills/java-development/`).
2. Lists the directory to confirm `SKILL.md` is present.
3. Reports success — you then restart the session (or it reloads) so the skill is picked up.

**Even easier — one line for each tool:**

| Tool | Paste this into the chat |
|------|--------------------------|
| Claude Code | `Clone https://github.com/zander-zyx/java-development-skill into ~/.claude/skills/java-development and confirm SKILL.md is there.` |
| Codex | `Clone https://github.com/zander-zyx/java-development-skill into ~/.codex/skills/java-development and confirm SKILL.md is there.` |
| OpenCode | `Clone https://github.com/zander-zyx/java-development-skill into ~/.opencode/skills/java-development and confirm SKILL.md is there.` |
| ZCode | `Clone https://github.com/zander-zyx/java-development-skill into ~/.zcode/skills/java-development and confirm SKILL.md is there.` |

> If the GitHub URL is slow, tell the agent the mirror instead: `https://gitee.com/zdking_project/java-development-skill.git` (China) or `https://cnb.cool/zdking/java-development-skill`.

### Option 3 — Manual install for one tool

If you prefer not to run a script, clone the repo directly into your tool's skill directory. Each tool looks in a different folder under your home:

| Tool | Skill path | Command |
|------|-----------|---------|
| **Claude Code** | `~/.claude/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.claude/skills/java-development` |
| **OpenAI Codex** | `~/.codex/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.codex/skills/java-development` |
| **OpenCode** | `~/.opencode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.opencode/skills/java-development` |
| **ZCode** | `~/.zcode/skills/java-development/` | `git clone https://github.com/zander-zyx/java-development-skill.git ~/.zcode/skills/java-development` |

That single `git clone` is the whole install. No build step, no config edit.

### Option 4 — Project-level install (only one project)

Want the skill active inside one Java project, not globally? Clone into the project's local tool directory:

```bash
# inside your Java project root, pick your tool:
git clone https://github.com/zander-zyx/java-development-skill.git .claude/skills/java-development
# or:  .codex/skills/java-development
#      .zcode/skills/java-development
#      .opencode/skills/java-development
```

Project-level skills take priority over user-level, so this also overrides a global install for that project only.

### Option 5 — Read the rules without any tool

The `*.md` files are plain Markdown. Browse them on GitHub/Gitee/cnb, or clone and read locally. Copy individual rules into your team wiki. No AI tool required.

### Verify the install worked

**30-second check** — open a fresh session in your tool (the skill loads at startup, so restart if it was already running) and paste:

```
How do I prevent N+1 queries in JPA?
```

You should get an answer that specifically mentions **JOIN FETCH / EntityGraph** and the `open-in-view = false` setting — those come from `spring-boot/sb-jpa-repository.md`. If the answer is generic ("use lazy loading…"), the skill didn't load; see [Troubleshooting](#-troubleshooting) below.

## 💡 How to use

You don't "open" or "invoke" the skill. Once installed, it works **transparently** in the background of every Java-related conversation.

### The mental model

```
You type a Java question
        │
        ▼
The tool reads SKILL.md's description (the trigger metadata)
        │
        ├── keywords match (@RestController, OOM, MyBatis-Plus, …)
        │     └── tool loads SKILL.md's lightweight route table
        │           └── tool loads only the specific rule file(s) needed
        │                 └── answer follows those conventions
        │
        └── no match → tool answers with its general knowledge (skill stays silent)
```

You never type a file name. The skill decides what to load based on what you said.

### Where to use it

- **Inside your Java project** — `cd` into your project, launch the tool there. It sees your `pom.xml` / source files *and* has the skill loaded. Best results.
- **In any folder** — the skill is user-global (after Option 1/2). You can ask Java questions even outside a project; the skill still applies, the tool just can't see your code.

### What to ask — trigger examples

The `description` frontmatter catches broad Java/Spring/JVM signals; the route table in `SKILL.md` then picks the smallest useful rule set. Some natural prompts that fire the skill:

| You say… | Skill loads… |
|----------|--------------|
| *"Write a JPA repository for Order, watch out for N+1"* | `spring-boot/sb-jpa-repository.md` (→ JOIN FETCH / EntityGraph) |
| *"My MyBatis-Plus pagination returns all rows"* | `spring-boot/sb-mybatis-plus.md` (→ forgot `PaginationInnerInterceptor`) |
| *"Review this class for thread safety"* | `code-review/cr-concurrency.md` + `code-review/cr-resource-leak.md` |
| *"Set up Testcontainers with MySQL"* | `testing/test-testcontainers.md` (→ `@ServiceConnection`) |
| *"Prod is OOMing, how do I find the leak?"* | `jvm/jvm-oom-analysis.md` (→ heap dump + MAT) |
| *"Migrating from Spring Boot 2.7 to 3"* | `spring-boot/sb-migration-2-to-3.md` (→ 6 breaking changes) |
| *"帮我写个 OrderService，保存订单+调支付"* | `spring-boot/sb-dependency-injection.md` + `spring-boot/sb-mybatis-plus.md` (中文 also triggers) |

See [`examples/usage-examples.md`](examples/usage-examples.md) (or [中文版](examples/usage-examples.zh.md)) for full prompts with the actual output each produces.

### Force-loading when auto-trigger misses

If a prompt should have triggered the skill but didn't (rare — usually means an unusual phrasing), force it:

| Tool | Command |
|------|---------|
| **Claude Code** | `/skill java-development` then your prompt (or it auto-loads on next Java mention) |
| **Codex** | `/skill java-development <your prompt>` |
| **ZCode** | `/skill java-development <your prompt>` |
| **OpenCode** | the `skill` tool is invoked by the agent automatically; rephrase with a keyword from the description |

### Keeping the skill up to date

The skill evolves. To pull new rules and rule updates:

```bash
cd ~/.claude/skills/java-development    # or wherever you cloned it
git pull
```

If you used the installer (which symlinks), `git pull` in the original clone updates **all** tools at once — they share the same source.

## 🛠 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Skill doesn't trigger on a Java question | Tool session was running before install | Restart the tool (skill loads at startup) |
| `./install.sh: Permission denied` | Script not executable | `chmod +x install.sh` then retry |
| Installer reports "No AI tool config directories found" | None of `.claude` / `.codex` / `.opencode` / `.zcode` exist yet | Install a tool first (see [Prerequisites](#prerequisites)), or run `./install.sh --force` to create the paths |
| Windows: `ln: failed to create symbolic link` | No symlink privilege | The installer auto-falls back to a copy; or run Git Bash **as Administrator** |
| `git pull` says "detached HEAD" after installer | You're in the wrong directory | The installer symlinks; `cd` into the original clone (the symlink target), not the link, to pull |
| Codex loads the skill but ignores rules | Codex uses `AGENTS.md` for *always-on* instructions, `SKILL.md` for *on-demand* | This is expected — the skill is on-demand by design. Rephrase with a trigger keyword |
| Updated the repo but tool still uses old rules | Tool caches skills per session | Restart the tool session |

If something else breaks, [open an issue](https://github.com/zander-zyx/java-development-skill/issues) with the tool name, OS, and the exact command + output.

## 🎨 Code Style Baseline

Every example in this skill follows the same conventions, so generated code is consistent:

| Aspect | Convention |
|--------|-----------|
| **Dependency injection** | Constructor injection via `final` fields + `@RequiredArgsConstructor` (never field `@Autowired`) |
| **Logging** | Lombok `@Slf4j` + SLF4J (never `System.out.println`) |
| **DTOs** | Java `record` (immutable, no Lombok needed) |
| **Entities** | Lombok `@Data` (mutable, with id-based `equals`/`hashCode` — see `code-review/cr-equals-hashcode.md`) |
| **Persistence** | **MyBatis-Plus** by default (China mainstream); JPA as optional reference |
| **Spring Boot** | 3.x (`jakarta.*`, Java 17+); 2.x differences in `spring-boot/sb-migration-2-to-3.md` |
| **Build** | Maven |

## 📑 Rule Index

<details>
<summary><b>🌱 Spring Boot Development (9 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `spring-boot/sb-dependency-injection.md` | HIGH | Constructor injection, Lombok allowlist, Bean lifecycle |
| `spring-boot/sb-project-structure.md` | HIGH | Package-by-feature layering |
| `spring-boot/sb-config-profiles.md` | MEDIUM | application.yml, profiles, `spring.config.import` |
| `spring-boot/sb-mybatis-plus.md` ⭐ | HIGH | BaseMapper/IService, LambdaQueryWrapper, pagination, logical delete |
| `spring-boot/sb-jpa-repository.md` | MEDIUM | N+1, @Transactional, lazy loading, Hibernate 6 UUID |
| `spring-boot/sb-exception-handling.md` | HIGH | @RestControllerAdvice, RFC 7807 ProblemDetail |
| `spring-boot/sb-rest-client.md` | MEDIUM | RestClient vs RestTemplate (deprecated) vs WebClient |
| `spring-boot/sb-actuator-health.md` | MEDIUM | Actuator, Micrometer, distributed tracing |
| `spring-boot/sb-migration-2-to-3.md` ⭐ | HIGH | 2.x ↔ 3.x migration (6 breaking changes) |

</details>

<details>
<summary><b>🔍 Java Code Review (6 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `code-review/cr-concurrency.md` | HIGH | synchronized, locks, race conditions, atomic classes, virtual threads |
| `code-review/cr-resource-leak.md` | HIGH | try-with-resources, streams, connections, locks |
| `code-review/cr-null-safety.md` | HIGH | Optional usage, @Nullable, NPE defense |
| `code-review/cr-equals-hashcode.md` | MEDIUM | equals/hashCode contract, records, entity equality |
| `code-review/cr-stream-pitfalls.md` | MEDIUM | parallel stream, reuse, shared mutation |
| `code-review/cr-anti-patterns.md` | MEDIUM | magic values, swallowed exceptions, logging abuse |

</details>

<details>
<summary><b>🧪 Java Testing (6 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `testing/test-layering.md` | HIGH | Unit / slice / integration test pyramid |
| `testing/test-junit5.md` | HIGH | JUnit 5 lifecycle, parameterized tests, extensions |
| `testing/test-mockito.md` | HIGH | Stub/spy/verify, argument matchers, static mocking |
| `testing/test-testcontainers.md` ⭐ | HIGH | @ServiceConnection, real DB boundaries, container reuse |
| `testing/test-spring-boot-test.md` | HIGH | @WebMvcTest / @DataJpaTest / @SpringBootTest slices |
| `testing/test-coverage-assertj.md` | MEDIUM | AssertJ fluent assertions, JaCoCo coverage |

</details>

<details>
<summary><b>🔥 JVM Troubleshooting (5 rules)</b></summary>

| Rule | Impact | Covers |
|------|--------|--------|
| `jvm/jvm-gc-tuning.md` | HIGH | G1 / ZGC / Parallel selection, heap sizing |
| `jvm/jvm-oom-analysis.md` | HIGH | Heap dump on OOM, MAT dominator tree, leak patterns |
| `jvm/jvm-thread-dump.md` | HIGH | Deadlock detection, blocked threads, thread leaks |
| `jvm/jvm-cpu-high.md` | HIGH | top -Hp + jstack + async-profiler flame graphs |
| `jvm/jvm-gc-logs.md` | MEDIUM | -Xlog:gc* interpretation, GCEasy |

</details>

## 🤝 How to Contribute

This is a personal skill but PRs are welcome. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide (rule file structure, code style, commit conventions, in English and 中文).

Quick summary:

1. **Typo / clarification** — direct PR, no discussion needed.
2. **New rule** — open an issue first to discuss scope. Follow the existing file structure: frontmatter (`title` / `impact` / `tags` / `description`) + sections (`Why it matters` / `Correct` / `Incorrect` / `Context`).
3. **Updated framework behavior** — Java/Spring evolves fast. If a rule is outdated for the current version, PR the fix and note the version in `Context`.

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to abide by its terms.

See `metadata.json` for the version this skill was authored against.

## 📜 License

MIT — see [LICENSE](LICENSE). Free to use, modify, distribute. Attribution appreciated but not required.

---

**Authored**: July 2026 · **Target**: Spring Boot 3.x + Java 17/21 · **Persistence default**: MyBatis-Plus
