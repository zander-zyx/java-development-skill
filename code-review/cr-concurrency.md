---
title: Concurrency and Thread Safety
impact: HIGH
impactDescription: Concurrency bugs are non-deterministic — they pass tests and fail in prod under load, the hardest class to debug
tags: concurrency, thread-safety, synchronized, lock, race-condition, atomic, threadlocal
description: Audit for shared mutable state; use immutable/atomic/thread-confined data; check lock ordering and @Transactional proxy bypass
alwaysApply: true
---

## Concurrency and Thread Safety

Concurrency defects are the worst kind: tests pass, the app runs fine in QA, then corrupts data under prod load. Audit shared mutable state ruthlessly.

### Why it matters

- **Non-deterministic** — race conditions depend on thread scheduling; you can't reproduce them by re-running the test.
- **Silent corruption** — a missing `volatile` or wrong lock produces wrong numbers, not exceptions. Data integrity breaks quietly.
- **Hard to fix late** — adding synchronization to existing code often introduces deadlocks or kills throughput. Design for it up front.

### The hierarchy of safety (prefer top)

1. **Immutable / stateless** — no shared state, no bug. Use `record`, `final` fields, return new instances instead of mutating.
2. **Thread-confined** — state lives in one thread (local vars, `ThreadLocal`). No sharing, no bug.
3. **Concurrent primitives** — `AtomicInteger`, `ConcurrentHashMap`, `BlockingQueue`. Correct by construction.
4. **Explicit locking** — `synchronized` or `Lock`. Last resort; easy to get wrong.

### Correct — immutable by default

```java
// immutable + stateless → trivially thread-safe
public record OrderTotal(BigDecimal subtotal, BigDecimal discount, BigDecimal tax) {
    public BigDecimal grandTotal() {
        return subtotal.subtract(discount).add(tax);
    }
}
```

### Correct — atomic for counters

```java
private final AtomicLong orderCounter = new AtomicLong();

public long nextOrderSeq() {
    return orderCounter.incrementAndGet();
}
```

### Correct — concurrent collections

```java
// ✅ thread-safe
private final Map<Long, Order> cache = new ConcurrentHashMap<>();

// ❌ HashMap under concurrent put → lost updates, infinite loops on resize (linked-list cycle, a real JDK bug history)
private final Map<Long, Order> badCache = new HashMap<>();
```

### Correct — synchronized only when needed

```java
private final Object lock = new Object();
private int available;

public void reserve(int qty) {
    synchronized (lock) {                          // lock a private final object, not `this`
        if (available < qty) throw new InsufficientStockException();
        available -= qty;
        // ...
    }
}
```

Prefer `java.util.concurrent.locks.ReentrantLock` if you need tryLock/timeout/fairness; otherwise `synchronized` is simpler.

### Incorrect — the classic races

**Check-then-act on a plain field**:
```java
// ❌ TOCTOU race: two threads both pass the null check, both init
private Helper helper;
public Helper getHelper() {
    if (helper == null) helper = new Helper();
    return helper;
}
```
Fix: `synchronized` on the method, declare `volatile` + double-checked locking *very carefully*, or — best — eager-init `private final Helper helper = new Helper();`.

**Lazy double-checked locking without volatile**:
```java
// ❌ broken: another thread can see a non-null helper whose constructor hasn't finished
private static Helper instance;                    // missing volatile
public static Helper getInstance() {
    if (instance == null) {
        synchronized (Helper.class) {
            if (instance == null) instance = new Helper();
        }
    }
    return instance;
}
```
Fix: `private static volatile Helper instance;`.

**Modifying a collection while iterating**:
```java
// ❌ ConcurrentModificationException (single-threaded) or undefined behavior (concurrent)
for (Order o : orders) {
    if (o.isCancelled()) orders.remove(o);
}
```
Fix: `orders.removeIf(Order::isCancelled);` or iterate the iterator's `.remove()`.

### Lock ordering and deadlock

If two code paths each acquire two locks in opposite orders, you get a deadlock:

```java
// Thread A: lock1 then lock2     Thread B: lock2 then lock1 → deadlock
```

**Rules**:
- Acquire locks in a **consistent global order** across the codebase.
- Hold locks for the **shortest time** possible.
- **Don't** call external code (callbacks, overridable methods) while holding a lock — you don't know what locks it'll take.
- **Don't** acquire a second lock if you can avoid it; refactor to one lock.

### ThreadLocal — and why to be careful

`ThreadLocal` is thread-confined storage — great for per-request context (user, trace), but it has a footgun in **thread pools**:

```java
private static final ThreadLocal<UserContext> CTX = new ThreadLocal<>();

@Deprecated // example of the leak
public void handle(UserContext ctx) {
    CTX.set(ctx);
    try {
        // ... work ...
    } finally {
        CTX.remove();                              // ✅ MUST remove or the next task on this pooled thread sees stale ctx
    }
}
```

Forget `remove()` and a pooled thread reuses the previous user's context → security leak. Prefer `try-finally` with `remove()` always, or use scoped values (Java 21+) instead.

### Virtual threads (Java 21+) — new caveats

```java
// Java 21: virtual threads dramatically increase concurrency
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> fetch(url(i))));
}
```

Two review points:
- **Never pool virtual threads** — they're cheap; one per task. Using a fixed pool defeats their purpose.
- **`synchronized` blocking a virtual thread pins the carrier** — prefer `ReentrantLock` in code that runs on virtual threads, so the carrier can move on during IO. (JDK 21+ has some pinning fixes; verify on your JDK.)

### @Transactional proxy bypass (cross-cutting)

Spring's `@Transactional` uses a proxy — self-invocation bypasses it:

```java
@Service
public class OrderService {
    public void batch() {
        for (Order o : orders) place(o);           // ❌ direct call bypasses @Transactional proxy
    }
    @Transactional
    public void place(Order o) { repo.save(o); }
}
```
The `place` call is `this.place()`, not through the proxy → no transaction. Fix: split into two beans, or inject self via `@Autowired OrderService self; self.place(o)`.

### Concurrency review checklist

When reviewing Java code, flag:
- [ ] Mutable shared field that's not `final`, `volatile`, or guarded by a lock?
- [ ] Plain `HashMap`/`ArrayList` used across threads (vs `ConcurrentHashMap`/`CopyOnWriteArrayList`)?
- [ ] Double-checked locking without `volatile`?
- [ ] `ThreadLocal.set()` without a `try-finally remove()`?
- [ ] Two locks acquired with no obvious ordering?
- [ ] `synchronized` over a long IO call (DB, HTTP) — holds the lock too long?
- [ ] Self-invocation of `@Transactional` methods?
- [ ] On Java 21+: `synchronized` inside code likely to run on virtual threads?

### Context

- **Java Memory Model**: `volatile` guarantees visibility and prevents instruction reordering; it does NOT make `++` atomic. Use `Atomic*` for compound actions.
- **`synchronized(this)`** vs `synchronized(lock)`: locking `this` exposes your lock to external callers who might lock you too. Use a private final lock object.
- **Cross-ref**: lock-held-too-long ties to `spring-boot/sb-jpa-repository.md` transactions; `ThreadLocal` removal pattern relates to the cleanup rule in `code-review/cr-resource-leak.md`.
