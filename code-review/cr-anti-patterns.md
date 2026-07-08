---
title: General Anti-Patterns
impact: MEDIUM
impactDescription: Catch-all review rules: magic values, swallowed exceptions, log abuse, mutable statics, premature optimization
tags: anti-patterns, magic-values, exceptions, logging, static, review
description: Catch-all review checklist for magic values, swallowed exceptions, log abuse, mutable static, instanceof chains
alwaysApply: true
---

## General Anti-Patterns

The catch-all code-review rules that don't fit a single topic but show up constantly. Run this checklist over any code that doesn't trigger the concurrency/resource/null/equals/stream rules.

### Magic values

```java
// ❌
if (order.getStatus() == 3) { ... }

// ✅ named constant or enum
if (order.getStatus() == Status.PAID.getCode()) { ... }

// ✅ better — enum
public enum Status { CREATED, PAID, SHIPPED, CANCELLED }
if (order.getStatus() == Status.PAID) { ... }
```

Even strings: `"PAID"` scattered across files is a typo waiting to happen. Define an enum or constant once. Numbers are worse — `3` means nothing to a reader.

### Swallowed exceptions

```java
// ❌ the bug becomes invisible
try {
    placeOrder(req);
} catch (Exception e) {
    // nothing
}

// ❌ logged but not propagated — caller has no idea it failed
try {
    placeOrder(req);
} catch (Exception e) {
    log.error("error", e);
}

// ✅ either propagate, or handle meaningfully
try {
    placeOrder(req);
} catch (PaymentDeclinedException e) {
    log.warn("Payment declined for order", e);
    return ResponseEntity.badRequest().body(...);
}
// let unexpected exceptions bubble to the global handler
```

If you catch and don't act, the next person debugging wonders why the system silently misbehaves. Either handle it (recover / map to a domain outcome) or don't catch it.

### Catching `Exception` / `Throwable` too broadly

```java
// ❌ catches NullPointerException, OutOfMemoryError sibling errors, everything
try { ... } catch (Exception e) { ... }
```

Catch the **specific** exception you can handle. Catching `Exception` masks programmer errors (NPE) as if they were business failures.

### Logging abuse

```java
// ❌ string concat — always evaluated even if level disabled
log.debug("Order " + order.getId() + " for " + user.getName());

// ✅ parameterized — only formatted if level enabled
log.debug("Order {} for {}", order.getId(), user.getName());

// ❌ logging inside a hot loop at INFO
for (Order o : orders) log.info("Processing " + o.getId());

// ✅ one summary log
log.info("Processing {} orders", orders.size());
```

Rules:
- Use `{}` placeholders, never string concatenation.
- Don't log sensitive data (passwords, full card numbers, PII).
- Don't log at INFO inside hot loops — aggregate.
- Don't log and rethrow — the caller will log it again, double-logging is noise.

```java
// ❌ double-log
try { ... } catch (Exception e) { log.error("...", e); throw e; }
```

### Mutable static state

```java
// ❌ global mutable state — concurrency hazard, untestable
private static Map<String, Config> CACHE = new HashMap<>();
public static Config get(String key) {
    return CACHE.computeIfAbsent(key, this::load);   // not thread-safe
}
```

Static mutable state is shared across all threads (see `code-review/cr-concurrency.md`), survives between tests (pollution), and makes the code impossible to mock. Inject as a bean instead.

### `instanceof` chains where polymorphism belongs

```java
// ❌ every new type means editing this method
if (animal instanceof Dog) { bark(); }
else if (animal instanceof Cat) { meow(); }
else if (animal instanceof Bird) { chirp(); }

// ✅ polymorphism
animal.makeSound();                                 // each subtype implements
```

### Empty catch block with comment

```java
// ❌ "intentional" is not a justification — at minimum log
try { Thread.sleep(100); } catch (InterruptedException e) { }
```
Interruption has a contract: restore the interrupt status. `catch (InterruptedException e) { Thread.currentThread().interrupt(); }` — or you break cancel semantics.

### Returning a Boolean object that can be null

```java
// ❌ caller NPEs on unboxing
public Boolean isValid(Order o) {
    if (o == null) return null;
    return o.getStatus() == Status.PAID;
}

// ✅ primitive boolean — can't be null
public boolean isValid(Order o) {
    return o != null && o.getStatus() == Status.PAID;
}
```

### Premature optimization / "clever" code

```java
// ❌ bit tricks that no reviewer understands
int avg = (a + b) >>> 1;                           // also overflows for large a+b!

// ✅ readable and correct
int avg = (int) ((long) a + b) / 2;
```

Optimize when you have a measured bottleneck. Most code is IO-bound; "clever" CPU tricks add bugs without speedups.

### Using `==` for object identity when equals is meant

```java
// ❌ BigInger/BigDecimal/String — == compares references
if (amount == BigDecimal.ZERO) { ... }

// ✅
if (amount.compareTo(BigDecimal.ZERO) == 0) { ... }   // BigDecimal.equals scales: 1.0 != 1.00
// or for value comparison ignoring scale:
if (amount.signum() == 0) { ... }
```

Note: `BigDecimal.equals` returns false for `1.0` vs `1.00` (different scales). Use `compareTo(...) == 0` for value equality.

### Empty/no-op method overriding

```java
// ❌ overriding a method to do nothing — why?
@Override public void close() { }
```
Either implement correctly or don't override. Empty overrides usually mean a misunderstanding of the contract.

### Mutable enums / leaking enum internals

```java
// ❌ enum with mutable state
public enum Counter { INSTANCE; private int n; public void inc() { n++; } }
```
Enums are singletons; mutable enum state is global mutable state. Keep enums immutable.

### Review checklist

- [ ] Numeric or string literal that should be a constant/enum?
- [ ] Empty catch, or catch-then-log-and-continue without recovery?
- [ ] Catch of `Exception`/`Throwable` instead of a specific type?
- [ ] String concatenation in log statements?
- [ ] Sensitive data in log output?
- [ ] Static mutable field?
- [ ] `instanceof` chain that polymorphism would replace?
- [ ] Empty `InterruptedException` catch without restoring interrupt?
- [ ] `==` on `BigDecimal`/`String`/boxed types where `.equals` is meant?
- [ ] BigDecimal equality via `.equals` (scale trap)?

### Context

- **This file is the catch-all**. When reviewing code that doesn't trigger the topic-specific rules (`cr-concurrency`, `cr-resource-leak`, `cr-null-safety`, `cr-equals-hashcode`, `cr-stream-pitfalls`), run through this checklist.
- **Project-specific rules**: if the project has lint configs (Checkstyle, SpotBugs, Error Prone), respect them — they encode these rules automatically.
- **Cross-ref**: shared mutable static is detailed in `code-review/cr-concurrency.md`; logging in async/reactive context relates to `spring-boot/sb-actuator-health.md` (MDC + traceId).
