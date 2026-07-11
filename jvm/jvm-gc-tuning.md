---
title: GC Selection and Tuning
impact: HIGH
impactDescription: Right GC + heap sizing prevents stop-the-world pauses that break SLAs
tags: gc, g1, zgc, parallel, heap-sizing, pauses, latency
description: Tune GC only from measured latency, throughput, allocation, live-set, and container evidence; preserve modern JVM ergonomics unless data justifies a change
---

## GC Selection and Tuning

Most apps need no tuning — Java's defaults are good. Reach for GC tuning only when you measure pause/throughput problems, and start with selection and heap sizing, not flag micro-tuning.

### Why it matters

- **STW pauses break latency SLAs** — a 200ms GC pause means 200ms p99 spike for every concurrent request.
- **Collector trade-offs are workload-specific** — throughput, pause time, CPU, memory overhead, allocation rate, and heap size interact.
- **Micro-tuning flags are a trap** — most "tuning" blog posts don't apply to your workload. The wins are in GC choice + heap sizing.

### The GC options (Java 17/21)

| GC | Use when | Pause | Throughput | Memory overhead |
|----|----------|-------|-----------|-----------------|
| **G1** (HotSpot default since Java 9) | General-purpose balance | Bounded-goal, workload dependent | High | Moderate |
| **ZGC** | Very low pause goals and enough CPU/memory headroom | Very low, workload dependent | Lower than throughput collectors | Higher |
| **Parallel** | Batch/throughput where long pauses are acceptable | Potentially long | High | Low |
| **Serial** | Small heaps or constrained single-CPU environments | Potentially long | Low | Lowest |
| Shenandoah | Low-pause collector in supporting OpenJDK distributions | Low, workload dependent | Moderate | Moderate |

Enable: `-XX:+UseG1GC`, `-XX:+UseZGC`, `-XX:+UseParallelGC`, `-XX:+UseSerialGC`.

### Default to G1

G1 is HotSpot's default general-purpose collector and is a sound starting point when measurements do not justify another collector. Keep the runtime default unless the service has a documented throughput or latency requirement that the current collector misses.

### When to switch to ZGC

Evaluate ZGC when pause time is the dominant constraint, the current collector misses the measured SLA, and the service has enough CPU/memory headroom. Benchmark with production-like allocation and live-set behavior; do not select it from heap size alone.

```
-XX:+UseZGC
-XX:SoftMaxHeapSize=<N>g  # soft target; ZGC grows beyond if needed
```

Generational ZGC is available in JDK 21, became the default ZGC mode in JDK 23, and the non-generational mode was removed in JDK 24. Add `-XX:+ZGenerational` only on a runtime that supports and needs that selector; do not carry obsolete flags across JDK upgrades.

### Step 1: Size the heap first

```
-Xms1g -Xmx4g             # example only; derive both values from evidence
```

Set `-Xms` equal to `-Xmx` only when predictable latency and reserved memory are more important than elasticity. In shared/container environments, a smaller `-Xms` can reduce committed memory. Size `-Xmx` from the measured live set, allocation bursts, native memory, replica count, and container limit.

Don't over-size: a 32GB heap on a service with 2GB live data just makes GC pauses longer (more to scan) and uses container memory.

### Step 2: Set the pause-time goal (G1)

```
-XX:MaxGCPauseMillis=200   # G1 tries to keep pauses under this
```

This is a *goal*, not a guarantee. G1 adjusts young-gen size to meet it. If your pauses exceed it consistently, the goal may be unrealistic for your heap — either accept longer pauses or increase heap / switch to ZGC.

### Step 3: Container memory limits

In Docker/K8s, `-XX:+UseContainerSupport` is enabled by default on modern JDKs. Ensure `-Xmx` is below the container limit and leave headroom for metaspace, code cache, direct buffers, thread stacks, GC structures, JNI/native libraries, and the process itself. A percentage such as 70-80% can be an initial experiment, not a universal rule:

```
# 4GB container: start conservatively, then verify native + heap peaks
-Xms1g -Xmx3g
```

Do not cap metaspace, direct memory, or thread stacks with copied values unless measurements and failure-mode tests justify those limits; arbitrary caps can create a different OOM.

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
- **Full GC happening?** Inspect the logged cause, old-generation occupancy, humongous allocations, metaspace/class loading, explicit GC, and allocation pressure before choosing a fix. See `jvm/jvm-gc-logs.md`.

### Common anti-patterns

**Heap too big**: a much larger heap than the measured live set can waste memory and delay reclamation. Collector behavior differs, so validate with logs rather than applying a fixed live-set multiplier.

**Automatic `-Xms == -Xmx` rule**: fixed heaps improve predictability but reserve memory and reduce elasticity. Choose deliberately for the deployment model.

**Chasing flags**: applying `-XX:+UseStringDeduplication`, `-XX:+AggressiveOpts` (removed), `-XX:+UseFastAccessorMethods` (removed) without measuring. Most "magic flag" blog posts are outdated or wrong.

**Parallel GC on a latency-sensitive service**: high throughput, long pauses. Switch to G1 or ZGC.

### Sample production JVM args (G1, general purpose)

```
-Xms1g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

### Sample (ZGC, low-latency large heap, JDK 21+)

```
-Xms4g -Xmx16g
-XX:+UseZGC
-XX:SoftMaxHeapSize=14g
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

### Review checklist

When tuning GC:
- [ ] GC choice matches the workload (G1 default, ZGC for low-latency large heap)?
- [ ] `-Xms`/`-Xmx` choice matches fixed-reservation versus elasticity needs?
- [ ] Heap sized from live-set, allocation-burst, and native-memory evidence?
- [ ] Heap leaves measured headroom under the container/process limit?
- [ ] Pause-time goal set for G1?
- [ ] GC logging enabled (`-Xlog:gc*`) for diagnosis?
- [ ] HeapDumpOnOutOfMemoryError set (relates to `jvm/jvm-oom-analysis.md`)?
- [ ] Changed one thing at a time, with measurement?

### Context

- **JDK baseline**: use an LTS/current release supported by the application and dependencies; revalidate collector flags on every runtime upgrade.
- **G1 ergonomics**: in modern JDKs G1 self-tunes well; resist overriding region size / IHOP unless measurement shows the default is wrong.
- **Cross-ref**: GC log interpretation in `jvm/jvm-gc-logs.md`; OOM (where GC tuning alone won't fix a leak) in `jvm/jvm-oom-analysis.md`; container sizing in `spring-boot/sb-config-profiles.md`.
