---
title: Stream API Pitfalls
impact: MEDIUM
impactDescription: Stream misuse causes silent wrong results, shared-mutable bugs in parallel, and one-shot stream errors
tags: stream, lambda, parallel-stream, functional, collect
description: Avoid parallel stream for most cases; don't reuse streams; don't mutate shared state in lambdas; understand side-effects
alwaysApply: true
---

## Stream API Pitfalls

The Stream API is expressive but has sharp edges. Four pitfalls account for most bugs: parallel stream misuse, stream reuse, shared-state mutation in lambdas, and `forEach` where a `collect` was meant.

### Why it matters

- **`parallelStream()` is rarely faster** and often **wrong** — the common pool is shared, side-effects break, and ordering is lost.
- **Streams are one-shot**. Reusing throws `IllegalStateException` at runtime, not compile time.
- **Shared mutable state in lambdas** reintroduces concurrency bugs in "functional" code that looks safe.

### Correct — sequential streams for almost everything

```java
List<OrderResponse> responses = orders.stream()
    .filter(o -> o.getStatus().equals("PAID"))
    .sorted(comparing(Order::getAmount).reversed())
    .map(this::toResponse)
    .toList();
```

For 99% of cases, sequential `stream()` is fast enough and correct.

### Correct — collect, don't forEach-mutate

```java
// ✅ functional: produce a new collection
Map<Status, List<Order>> byStatus = orders.stream()
    .collect(groupingBy(Order::getStatus));

// ❌ imperative mutation of an external map
Map<Status, List<Order>> bad = new HashMap<>();
orders.forEach(o -> bad.computeIfAbsent(o.getStatus(), k -> new ArrayList<>()).add(o));
```

The first is parallelizable, testable, and side-effect-free. The second only looks similar.

### Incorrect — parallelStream

```java
// ❌ parallel rarely helps; common ForkJoinPool shared with other parallel ops; ordering lost
List<String> upper = names.parallelStream().map(String::toUpperCase).toList();
```

When parallel *does* win: large collections (millions of elements) with CPU-heavy per-element work, no ordering requirement, no shared state. For typical web-app collections (<10k elements, light operations), parallel's overhead exceeds the gain and it competes for the shared pool — degrading other requests.

If you genuinely need parallelism, use a custom `ForkJoinPool` (submit a task that runs the parallel stream inside), so you don't block the shared common pool:

```java
var pool = new ForkJoinPool(4);
List<String> result = pool.submit(() ->
    bigList.parallelStream().map(this::heavyOp).toList()
).get();
```

### Incorrect — parallel stream with shared mutable state

```java
// ❌ race condition: ArrayList is not thread-safe; results silently lost
List<Order> paid = new ArrayList<>();
orders.parallelStream()
    .filter(o -> o.getStatus().equals("PAID"))
    .forEach(paid::add);
```
Even with a thread-safe collection, results are unordered and the "functional" style is misleading. Use `.collect(toList())` — the collector handles thread safety correctly.

### Incorrect — reusing a stream

```java
// ❌ streams are one-shot; second terminal op throws IllegalStateException
Stream<Order> s = orders.stream().filter(o -> o.isPaid());
long count = s.count();
List<Order> list = s.toList();                     // throws

// ✅ recreate, or use a supplier
Supplier<Stream<Order>> ss = () -> orders.stream().filter(Order::isPaid);
long count = ss.get().count();
List<Order> list = ss.get().toList();
```

Or just collect once and operate on the list.

### Incorrect — forEach used for its side effects on a "functional" pipeline

```java
// ❌ peek and forEach are for side effects; using them to mutate is fragile
orders.stream()
    .peek(o -> o.setProcessed(true))               // peek is documented as debug-only
    .map(this::toResponse)
    .forEach(System.out::println);
```

`peek`'s contract is intentionally weak (the JDK docs say it exists "primarily to support debugging"). Use it to inspect; don't rely on it for production logic.

### Incorrect — large collection in stream with blocking IO

```java
// ❌ 10000 orders, 10000 HTTP calls, sequentially; also blocks the carrier thread
orders.stream()
    .map(this::fetchStatus)                         // each does a blocking HTTP call
    .toList();
```
Streams hide the per-element cost. If the per-element op is IO, prefer an async/reactive approach (WebClient Flux, or batch the IO) rather than a stream.

### Correct — flatMap for one-to-many

```java
// ✅ flatten nested collections
List<OrderItem> allItems = orders.stream()
    .flatMap(o -> o.getItems().stream())
    .toList();
```

### Correct — Optional-friendly chain

```java
// ✅ Optional + stream composition
String label = orderRepo.findById(id)
    .map(Order::getUser)
    .map(User::getName)
    .map(String::toUpperCase)
    .orElse("UNKNOWN");
```

### Review checklist

- [ ] `parallelStream()` used? (Justify with measurement; default to `stream()`.)
- [ ] Stream assigned to a variable then used twice?
- [ ] `forEach`/`peek` mutating external state in a pipeline?
- [ ] Non-thread-safe collection touched inside a parallel stream?
- [ ] Per-element blocking IO inside a stream over a large collection?
- [ ] `collect(toList())` replaced with `forEach(list::add)`?
- [ ] A `.map` lambda that has side effects (logging aside)?

### Context

- **`.toList()` (Java 16+)** returns an unmodifiable list; `collect(toList())` returns a mutable `ArrayList`. Pick by mutability needs.
- **Stream characteristics**: operations like `sorted` lose the `SIZED` and `ORDERED` characteristics; downstream `limit` may behave unexpectedly. Not usually a problem, but worth knowing when results look wrong.
- **Cross-ref**: parallel stream concurrency bugs relate to `code-review/cr-concurrency.md`; Optional chain to `code-review/cr-null-safety.md`.
