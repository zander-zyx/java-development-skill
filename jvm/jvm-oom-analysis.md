---
title: OutOfMemoryError Analysis
impact: HIGH
impactDescription: OOM crashes the JVM; correct dump + analysis identifies the leak in minutes vs hours
tags: oom, heap-dump, mat, memory-leak, jmap
description: Capture heap dump on OOM; analyze with MAT dominator tree; classify by OOM message (heap/metaspace/direct-buffer)
---

## OutOfMemoryError Analysis

OOM kills the JVM. The fix is: capture a heap dump at the moment of failure, then read the dominator tree to find what's retaining the memory.

### Why it matters

- **Reproducing is hard** — OOM often needs prod load and hours/days to surface. You can't "just run it again with a debugger".
- **Without a dump, you're guessing** — and the guess is usually wrong (it's almost never where you think).
- **The heap dump is the evidence** — capture it on the first crash, or you lose the moment.

### Step 1: Capture a heap dump on OOM (do this BEFORE you need it)

Add to JVM args so the dump is written automatically on the first OOM:

```
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/oom-%p.hprof
```

`%p` includes the PID. Without this, when OOM hits you have no dump and must reproduce — possibly for days.

### Step 2: Capture a dump manually (live process)

If the app is degraded but not yet crashed, dump it:

```bash
# jmap (works on HotSpot, older JDKs)
jmap -dump:format=b,file=heap.hprof <pid>

# jcmd (preferred, JDK 8+)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# JDK 9+ — also via jhsdb
jhsdb jmap --binaryheap --pid <pid> --file heap.hprof
```

**Caveat**: a full heap dump pauses the JVM (can be seconds to minutes for multi-GB heaps). On a prod server, expect a brief stall.

### Step 3: Classify by the OOM message

The message tells you which memory area ran out — different fixes:

| Message | Area | Typical cause |
|---------|------|---------------|
| `Java heap space` | Heap | Memory leak, or genuinely too-large working set, or a giant collection/array |
| `GC Overhead limit exceeded` | Heap | GC spending >98% time reclaiming <2% — effectively exhausted |
| `Metaspace` | Metaspace | Class loader leak (dynamic class generation, undeployed apps in a container) |
| `Direct buffer memory` | Off-heap | NIO `ByteBuffer.allocateDirect` not released (Netty, NIO clients) |
| `Unable to create new native thread` | Native | Thread leak, or OS thread/process limit hit |
| `StackOverflowError` | Stack (not OOM but adjacent) | Infinite recursion |

The fix differs per type — increasing heap won't fix a metaspace or native-thread OOM.

### Step 4: Analyze with Eclipse MAT

Open the `.hprof` in **Eclipse MAT** (Memory Analyzer Tool). The two views that matter:

**1. Dominator Tree** — "who retains the most memory". Sort by **Retained Heap** (not shallow). The top row is the biggest retainer; usually the leak source or the legitimate largest cache.

```
Dominator Tree (sorted by Retained Heap)
└── java.util.HashMap @ 0x7a3e...   retained 1.2 GB
    └── java.util.ArrayList @ ...    retained 1.1 GB  ← suspect
        └── millions of Order objects                ← the leak
```

**2. Leak Suspects Report** — MAT's automated analysis. Run it (`Leak Suspects` from the report menu); it points at the most likely culprit.

**3. Histogram** — count of instances by class. If `byte[]` has 50M instances, that's the smoking gun.

### Step 5: Find the path from GC root

For a suspect object, right-click → **Path to GC Roots → exclude weak/soft references**. This shows what's keeping the object alive — the field/variable you forgot to clear.

Common GC roots:
- Static fields (the classic global-cache leak)
- Active thread stacks (local variables)
- Synchronized monitors held
- JNI global references

### Common leak patterns

**Static map as cache, no eviction**:
```java
// ❌ grows forever
private static final Map<String, byte[]> CACHE = new HashMap<>();
public byte[] get(String k) { return CACHE.computeIfAbsent(k, this::load); }
```
Fix: bound it (`Caffeine`, `LinkedHashMap` with `removeEldestEntry`).

**`ThreadLocal` not removed in a thread pool**:
```java
// ❌ pooled thread keeps the ThreadLocal entry of the previous task
ThreadLocal<UserContext> CTX = new ThreadLocal<>();
// missing finally { CTX.remove(); }
```
With one long-lived `ThreadLocal` key, each pooled thread can retain the last task's value and leak data across requests. Unbounded growth occurs when code creates many distinct `ThreadLocal` keys or stores values that themselves keep growing. Always remove values at the owning boundary.

**Listener/callback not deregistered**:
```java
// ❌ registered, never unregistered; the publisher holds the subscriber forever
eventBus.register(this);
```
The subscriber is retained by the publisher's listener list.

**InputStream/Connection not closed** — direct buffer or finalizer-queue buildup. See `code-review/cr-resource-leak.md`.

**Huge result set loaded in memory**:
```java
// ❌ loads 10M rows into a List
List<Order> all = mapper.selectList(null);
```
Stream/process in batches instead.

### Step 6: Verify the fix

After fixing, monitor:
- Heap usage over time should plateau, not grow unboundedly.
- GC frequency should stabilize.
- Run a long soak test (12-24h) with prod-like load — if the leak is fixed, heap returns to baseline after GC; if not, it climbs.

### Review checklist

When investigating OOM:
- [ ] Is `-XX:+HeapDumpOnOutOfMemoryError` set? (If not, set it now before the next crash.)
- [ ] Heap dump captured from the failing instance?
- [ ] OOM message read — heap / metaspace / direct buffer / native thread?
- [ ] MAT dominator tree inspected for top retainers?
- [ ] Path-to-GC-roots found the retaining reference?
- [ ] Common patterns checked: static cache, ThreadLocal, listeners, unclosed resources, huge result sets?
- [ ] Heap size sane for the workload? (Sometimes it's not a leak, just too-small heap.)

### Context

- **Heap dump size**: roughly equals live heap at capture. A 4GB heap produces ~4GB dump. Have disk space.
- **Sensitive data**: heap dumps contain object data — passwords, PII. Handle with the same care as logs; restrict access.
- **Cross-ref**: thread leaks cause "native thread" OOM — see `jvm/jvm-thread-dump.md`; resource leaks that build up to OOM in `code-review/cr-resource-leak.md`.
