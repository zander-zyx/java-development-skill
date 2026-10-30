---
title: Java Version Modernization
impact: HIGH
impactDescription: Java upgrades can break compilation, runtime flags, reflection, dependencies, containers, and CI even when source changes look small
tags: java, migration, modernization, java-8, java-11, java-17, java-21, java-25, toolchain
description: Modernize Java versions safely by separating language changes from runtime/build/dependency upgrades and preserving compatibility requirements
---

## Java Version Modernization

Use this when upgrading Java 8/11/17/21/25, introducing newer language features, changing compiler release, or modernizing old Java idioms.

### Why it matters

Java modernization is not just syntax cleanup. Production incidents from naive upgrades are common and varied: an app moved to JDK 17 fails at startup because Jackson or Hibernate reflects into `java.util` and hits `InaccessibleObjectException` until `--add-opens` is restored; a CI pipeline passes on JDK 11 but the runtime container still ships JDK 8, so `NoSuchMethodError` appears only in staging; Lombok or MapStruct built for an older JDK silently stops generating code after the compiler upgrade. Runtime images, bytecode target, reflection access, removed JDK modules, TLS defaults, GC flags, annotation processors, and dependencies can all fail independently — the build staying green proves none of them.

### Upgrade order

1. **Identify the real target**: build `release`, CI JDK, runtime container, production JVM, and downstream consumers.
2. **Upgrade build/toolchain first** without source refactors.
3. **Make tests green** on the new JDK.
4. **Upgrade incompatible dependencies** with evidence.
5. **Then modernize syntax** in small, reviewable changes.

### Rules

- Use `--release` / Maven `maven.compiler.release` / Gradle toolchains when possible.
- Do not use `var`, `record`, text blocks, switch expressions, or pattern matching unless the target Java version supports them.
- For Java 8 to 11+, check removed Java EE/JAXB modules and old JVM flags.
- For Java 8/11 to 17+, check strong encapsulation and reflective access warnings/errors.
- For Java 17 to 21+ (including Java 25+), apply the virtual-thread pitfalls below before adopting them.
- Update annotation processors such as Lombok and MapStruct before blaming the compiler.
- Preserve public API bytecode compatibility for libraries unless a major-version break is accepted.

### Correct modernization examples

Use `java.time` for new date/time code:

```java
Instant now = clock.instant();
LocalDate businessDate = LocalDate.now(clock);
```

Use `record` only when target and framework support it:

```java
public record UserSummary(Long id, String name) {}
```

### Correct — virtual threads (Java 21+)

Virtual threads shine for high-fan-out blocking I/O, but only with these constraints:

- **Never `synchronized` around blocking I/O in a virtual thread.** A pinned carrier thread blocks the whole scheduler FIFO; under load this looks like a thread-pool starvation outage. Use `ReentrantLock` instead — it parks the virtual thread without pinning.
- **Never pool virtual threads.** They are cheap; create one per task (`Executors.newVirtualThreadPerTaskExecutor()`), not a fixed pool.
- **Limit concurrency with a `Semaphore`, not a thread pool size.**

```java
// Bad (Avoid) — synchronized around blocking I/O pins the carrier thread
synchronized (lock) {
    order = repository.findByRef(ref);   // blocking JDBC call while pinned
}

// Good (Preferred) — ReentrantLock parks the virtual thread cleanly
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    order = repository.findByRef(ref);
} finally {
    lock.unlock();
}

// Good (Preferred) — one virtual thread per task, Semaphore for backpressure
private final Semaphore dbPermits = new Semaphore(50);
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Callable<Order> task : tasks) {
        dbPermits.acquire();
        executor.submit(() -> {
            try { return task.call(); } finally { dbPermits.release(); }
        });
    }
}
```

Also avoid heavy work or long `synchronized` sections in `ThreadLocal`-dependent frameworks until compatibility is verified, and remember thread pools sized for platform threads are usually wrong for virtual threads.

### When NOT to use

- Do not introduce new syntax into a module targeting Java 8/11.
- Do not combine a JDK upgrade with unrelated business refactors.
- Do not remove compatibility flags until staging proves dependencies no longer need them.
- Do not migrate a CPU-bound service to virtual threads — they help blocking I/O workloads, not computation.

### Verification

```bash
java -version
mvn -q -version
mvn -q test
./gradlew javaToolchains
./gradlew test
```

Also verify the runtime image or deployment base image, not only the local compiler.

### Context

- Cross-ref Maven release config in `build-tools/build-maven-dependencies.md`.
- Cross-ref Gradle toolchains in `build-tools/build-gradle-dependencies.md`.
- Cross-ref JVM tuning after runtime changes in `jvm/jvm-gc-tuning.md`.
