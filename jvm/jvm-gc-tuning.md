---
title: GC Selection and Tuning
impact: HIGH
impactDescription: Right GC + heap sizing prevents stop-the-world pauses that break SLAs
tags: gc, g1, zgc, parallel, heap-sizing, pauses, latency
description: Default to G1 (Java 9+); use ZGC for low-latency large heaps; size heap and pause goals before micro-tuning
alwaysApply: true
---

## GC Selection and Tuning

Most apps need no tuning — Java's defaults are good. Reach for GC tuning only when you measure pause/throughput problems, and start with selection and heap sizing, not flag micro-tuning.

### Why it matters

- **STW pauses break latency SLAs** — a 200ms GC pause means 200ms p99 spike for every concurrent request.
- **Wrong GC wastes hardware** — Parallel GC maximizes throughput but has long pauses; ZGC gives sub-ms pauses but uses more CPU/memory.
- **Micro-tuning flags are a trap** — most "tuning" blog posts don't apply to your workload. The wins are in GC choice + heap sizing.

### The GC options (Java 17/21)

| GC | Use when | Pause | Throughput | Memory overhead |
|----|----------|-------|-----------|-----------------|
| **G1** (default since Java 9) | General purpose, balanced | 10-200ms | High | Moderate |
| **ZGC** | Low-latency, heaps >4GB, sub-ms pauses needed | <1ms (Java 16+) | Moderate | Higher (~15%) |
| **Parallel** | Batch/throughput, no SLA on pause | Long (seconds) | Highest | Low |
| **Serial** | Single-CPU small heaps | Long | Low | Lowest |
| Shenandoah | Alternative low-latency (OpenJDK) | <10ms | Moderate | Moderate |

Enable: `-XX:+UseG1GC`, `-XX:+UseZGC`, `-XX:+UseParallelGC`, `-XX:+UseSerialGC`.

### Default to G1

G1 is the default and correct choice for ~90% of services. It splits the heap into regions, collects the most garbage-dense regions first ("garbage first"), and meets a configurable pause-time goal. For most web services you don't need anything else.

### When to switch to ZGC

Switch when **all** are true:
- Heap is large (typically >8GB, often 32GB+).
- You need sub-10ms pause even under load.
- You can afford ~15% more memory and CPU.

```
-XX:+UseZGC
-XX:+ZGenerational        # generational ZGC (JDK 21+), lower overhead than non-gen
-XX:SoftMaxHeapSize=<N>g  # soft target; ZGC grows beyond if needed
```

Generational ZGC (JDK 21+) is the recommended form — it splits young/old for better throughput.

### Step 1: Size the heap first

```
-Xms4g -Xmx4g             # set min == max to avoid resizing stalls
```

**Set `-Xms` equal to `-Xmx`** so the JVM never resizes the heap at runtime (resizing causes pauses and fragmentation). Size to your working set + headroom — typically 2-3x live data after a full GC.

Don't over-size: a 32GB heap on a service with 2GB live data just makes GC pauses longer (more to scan) and uses container memory.

### Step 2: Set the pause-time goal (G1)

```
-XX:MaxGCPauseMillis=200   # G1 tries to keep pauses under this
```

This is a *goal*, not a guarantee. G1 adjusts young-gen size to meet it. If your pauses exceed it consistently, the goal may be unrealistic for your heap — either accept longer pauses or increase heap / switch to ZGC.

### Step 3: Container memory limits

In Docker/K8s, set `-XX:+UseContainerSupport` (default on since Java 10) and ensure `-Xmx` is below the container limit. Leave headroom for off-heap (metaspace, direct buffers, thread stacks, JNI) — usually `-Xmx` at ~75-80% of container memory:

```
# 4GB container → ~3GB heap
-Xms3g -Xmx3g
-XX:MaxMetaspaceSize=256m
-XX:MaxDirectMemorySize=512m
-XX:ThreadStackSize=512k
```

Without headroom, the container OOM-kills the JVM (the OS kills before Java's GC can react).

### Step 4: Tune only after measuring

Use GC logs (see `jvm/jvm-gc-logs.md`) and metrics (`jvm.gc.pause` from Micrometer) to understand current behavior before changing anything. Then change ONE thing at a time and measure.

Common tunings (G1):
```
-XX:MaxGCPauseMillis=100
-XX:G1HeapRegionSize=8m        # power of 2; larger regions for large heaps
-XX:InitiatingHeapOccupancyPercent=45   # start marking cycle earlier
```

Don't apply these blindly — defaults in newer JDKs (especially 17/21) are often better than "tuned" flags copied from old blogs.

### Step 5: Tune for vs. tune against

The mistake is to tune flags you read about rather than your measured bottleneck:
- **Pause too long?** Reduce pause goal, increase heap, or switch to ZGC.
- **CPU too high in GC?** Check if you're thrashing (heap too small) — increase heap, or your objects aren't dying young (check allocation patterns).
- **Full GC happening?** Usually metaspace leak, or old-gen filling before young-gen collection can keep up. See `jvm/jvm-gc-logs.md`.

### Common anti-patterns

**Heap too big**: 32GB heap with 1GB live data. GC scans 32GB each cycle → long pauses. Size to 2-3x live data.

**`-Xms != -Xmx`**: heap grows at runtime under load, causing pause + fragmentation. Set them equal.

**Chasing flags**: applying `-XX:+UseStringDeduplication`, `-XX:+AggressiveOpts` (removed), `-XX:+UseFastAccessorMethods` (removed) without measuring. Most "magic flag" blog posts are outdated or wrong.

**Parallel GC on a latency-sensitive service**: high throughput, long pauses. Switch to G1 or ZGC.

### Sample production JVM args (G1, general purpose)

```
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

### Sample (ZGC, low-latency large heap, JDK 21+)

```
-Xms16g -Xmx16g
-XX:+UseZGC
-XX:+ZGenerational
-XX:SoftMaxHeapSize=14g
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

### Review checklist

When tuning GC:
- [ ] GC choice matches the workload (G1 default, ZGC for low-latency large heap)?
- [ ] `-Xms` == `-Xmx`?
- [ ] Heap sized to 2-3x live data, not wildly larger?
- [ ] Heap leaves headroom under container limit (~75-80%)?
- [ ] Pause-time goal set for G1?
- [ ] GC logging enabled (`-Xlog:gc*`) for diagnosis?
- [ ] HeapDumpOnOutOfMemoryError set (relates to `jvm/jvm-oom-analysis.md`)?
- [ ] Changed one thing at a time, with measurement?

### Context

- **Java 21 LTS**: recommended baseline — generational ZGC, virtual threads, G1 improvements.
- **G1 ergonomics**: in modern JDKs G1 self-tunes well; resist overriding region size / IHOP unless measurement shows the default is wrong.
- **Cross-ref**: GC log interpretation in `jvm/jvm-gc-logs.md`; OOM (where GC tuning alone won't fix a leak) in `jvm/jvm-oom-analysis.md`; container sizing in `spring-boot/sb-config-profiles.md`.
