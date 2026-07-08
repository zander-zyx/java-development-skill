---
title: Resource Leaks
impact: HIGH
impactDescription: Leaked streams/connections/locks exhaust file descriptors or pool slots and crash the JVM under load
tags: resource-leak, try-with-resources, stream, connection, lock, jdbc
description: Every Closeable/Lock/ThreadLocal must be released in finally; use try-with-resources; never rely on GC
alwaysApply: true
---

## Resource Leaks

Any resource you acquire (`InputStream`, `Connection`, `Lock`, `ThreadLocal`, `PreparedStatement`) must be explicitly released. The JVM/GC won't save you — file descriptors and DB connections are finite and exhaustion crashes the app under load.

### Why it matters

- **File descriptors** are OS-level and limited (~1024 default per process on Linux). Leaking one per request kills you at ~1k concurrent requests.
- **DB connections** in a pool (HikariCP default 10) are exhausted by a single leak — the whole app hangs on the 11th request waiting for a connection.
- **Locks** not released deadlock the next caller.
- **Symptoms are delayed**: works in dev (low traffic), hangs in prod (hours later). The leak is invisible in code review unless you look.

### The rule

Every acquisition needs a matching release in a `finally` block — or use **try-with-resources** which does it for you.

### Correct — try-with-resources

```java
// multiple resources, closed in reverse order, even on exception
public String readConfig(Path path) throws IOException {
    try (var reader = Files.newBufferedReader(path);
         var other = Files.newBufferedReader(otherPath)) {
        return reader.readLine();
    }                                              // both closed automatically
}
```

Any object implementing `AutoCloseable` (most IO, JDBC, locks since Java 5 via `Lock`'s wrapper) works.

### Correct — JDBC (the classic leak site)

```java
public Order findOrder(Connection conn, Long id) throws SQLException {
    String sql = "SELECT * FROM t_order WHERE id = ?";
    try (PreparedStatement ps = conn.prepareStatement(sql);
         ResultSet rs = ps.executeQuery()) {
        if (rs.next()) return map(rs);
        throw new OrderNotFoundException(id);
    }                                              // ps and rs closed even on exception
}
```

Note: in Spring/MyBatis-Plus apps you usually don't touch `Connection` directly — the framework manages it. But if you call raw JDBC, wrap everything.

### Correct — Lock in try-finally

`Lock` is not `AutoCloseable` by default (the supertype method is `close()`; `Lock` has `unlock()`). Use try-finally:

```java
Lock lock = ...;
lock.lock();
try {
    // critical section
} finally {
    lock.unlock();                                 // ALWAYS in finally
}
```

**Critical ordering**: acquire the lock BEFORE the `try`. If you write `try { lock.lock(); ... }` and `lock()` throws, `finally` calls `unlock()` on an unlocked lock → `IllegalMonitorStateException`. The Java compiler doesn't catch this.

### Correct — ThreadLocal

```java
ThreadLocal<UserContext> CTX = new ThreadLocal<>();
CTX.set(ctx);
try {
    // work
} finally {
    CTX.remove();                                  // or the next pooled-thread task sees stale ctx (security leak)
}
```

### Incorrect — common leak patterns

**Stream/Reader never closed on exception path**:
```java
// ❌ if readLine() throws, reader is never closed
public String read(Path p) throws IOException {
    BufferedReader reader = Files.newBufferedReader(p);
    return reader.readLine();                      // leak on exception
}
```

**Connection returned to pool only on happy path**:
```java
// ❌ exception in processOrder leaks the connection
Connection conn = dataSource.getConnection();
processOrder(conn);
conn.close();
```

**Lock acquired inside try**:
```java
// ❌ unlock() on a not-locked lock throws IllegalMonitorStateException if lock() threw
try {
    lock.lockInterruptibly();
    doWork();
} finally {
    lock.unlock();
}
```

### Spring/MP — usually safe, but watch the edges

In a Spring Boot + MyBatis-Plus app:
- `@Transactional` and MyBatis-Plus sessions release connections on method exit (including on exception) — generally safe.
- **Watch** raw `DataSource.getConnection()` calls — those you own.
- **Watch** `RestClient`/`WebClient` response bodies — `ResponseEntity` with a streaming body must be consumed or closed; otherwise the connection isn't returned to the pool.
- **Watch** `Files.lines(path)` (returns a `Stream` backed by a file) — must be in try-with-resources or it leaks the file handle:

```java
// ✅ Stream<Path> line stream in try-with-resources
try (Stream<String> lines = Files.lines(path)) {
    lines.filter(s -> s.startsWith("#")).forEach(System.out::println);
}
```

### Don't rely on finalize / Cleaner

```java
// ❌ don't depend on GC to close — timing unpredictable, may never run
public class Leaky implements AutoCloseable {
    private final InputStream in;
    @Override
    @Deprecated
    protected void finalize() throws Throwable { in.close(); }   // unreliable
}
```

Java 9+ deprecated `finalize`; Java 18+ it's disallowed by default. Use try-with-resources explicitly.

### Review checklist

When reviewing Java code, flag:
- [ ] Any `new XxxStream/Reader/Writer/Connection` not in try-with-resources?
- [ ] A method that returns an open `Stream`/`InputStream` — who closes it? Document or wrap.
- [ ] `lock.lock()` placed inside the `try` (vs before it)?
- [ ] `ThreadLocal.set()` without a matching `finally { remove() }`?
- [ ] Raw `DataSource.getConnection()` in service code (should usually go through the framework)?
- [ ] `ResponseEntity` from `RestClient` with a streaming body never consumed?
- [ ] `Files.lines(...)` used without try-with-resources?

### Context

- **Try-with-resources** was added in Java 7 — there's no excuse to use the old try-finally for `Closeable` resources now.
- **Effectively-final pattern variable** — in try-with-resources, the resource variable is implicitly final; you can't reassign it. If you need to transform before closing, do that inside the body.
- **`AutoCloseable` vs `Closeable`**: `AutoCloseable.close()` can throw any `Exception`; `Closeable.close()` throws `IOException`. Most things are `AutoCloseable`.
- **Cross-ref**: ThreadLocal removal ties to `code-review/cr-concurrency.md`; connection pooling tuning relates to `spring-boot/sb-config-profiles.md` (HikariCP) and `spring-boot/sb-mybatis-plus.md`.
