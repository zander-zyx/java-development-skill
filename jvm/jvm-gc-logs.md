---
title: GC Log Interpretation
impact: MEDIUM
impactDescription: GC logs tell you pause frequency, GC cause, and whether tuning helps — the diagnostic for memory pressure
tags: gc-logs, xlog, gceasy, pauses, memory-pressure
description: Enable -Xlog:gc* in prod; read pause times, GC cause, and old-gen occupancy; upload to GCEasy for visualization
---

## GC Log Interpretation

GC logs are the diagnostic for memory behavior: how often the JVM pauses, how long, and why. Enable them always in prod; read them when you have a memory or pause problem.

### Why it matters

- **Pauses show up here first** — a p99 latency spike almost always corresponds to a GC pause; the log tells you which kind.
- **Trends reveal leaks** — old-gen occupancy climbing over hours/days is the early warning of an OOM.
- **Cause codes** tell you why the GC ran — `Allocation Failure`, `System.gc()`, `Metadata GC Threshold`, etc.

### Enable GC logging (Java 9+ — unified logging)

```
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

- `gc*` — all GC-related tags (`gc`, `gc+heap`, `gc+task`, etc.).
- `:time,uptime,level,tags` — what each line shows.
- `filecount=10,filesize=50M` — rotate, keep 10 files of 50MB.

Java 8 used `-XX:+PrintGCDetails` (different syntax) — for SB3 / Java 17+, always use `-Xlog:gc*`.

### Sample G1 log lines

```
[2026-07-03T10:15:32.100+0000][uptime:12345s][info][gc,start] GC(42) Pause Young (Normal) (G1 Evacuation Pause)
[2026-07-03T10:15:32.135+0000][uptime:12345s][info][gc] GC(42) Pause Young (Normal) (G1 Evacuation Pause) 256M->64M(512M) 35.123ms
[2026-07-03T10:15:32.135+0000][info][gc,cpu] GC(42) User=0.05s Sys=0.01s Real=0.04s
```

What each part means:
- `GC(42)` — sequence number (42nd GC).
- `Pause Young (Normal) (G1 Evacuation Pause)` — type: young-gen collection, normal trigger, evacuating survivors.
- `256M->64M(512M)` — heap before → after (total). 256MB used dropped to 64MB, total heap 512MB.
- `35.123ms` — pause duration. This is the SLA-relevant number.
- `User=0.05s Sys=0.01s Real=0.04s` — CPU time (User+Sys across all GC threads) vs wall-clock. User+Sys >> Real = parallel (good); User+Sys ≈ Real = single-threaded GC.

### What to look for

**1. Pause frequency and duration**
- How often does a pause happen? Once per second under load? Once per minute?
- How long? <100ms is healthy for most services; >1s is a problem.
- Trends: increasing pause duration over time = heap filling or fragmentation.

**2. Heap occupancy before/after GC**
- After young GC, young-gen should be mostly empty.
- After old-gen GC, old-gen should drop. If old-gen **never drops** despite GC → memory leak (see `jvm/jvm-oom-analysis.md`).

**3. GC cause**
- `Allocation Failure` — normal young-gen trigger.
- `System.gc()` — somewhere in code calls `System.gc()`; remove it.
- `Metadata GC Threshold` — metaspace filling; class-loading leak.
- `Last ditch collection` — a full GC after a failed young GC; serious memory pressure.
- `Heap Inspection Initiated GC` — `jcmd GC.heap_info` or similar; not a problem.

**4. Concurrent cycle timing (G1)**:
- `[gc] GC(50) Concurrent Cycle` — the concurrent mark cycle. These don't pause (mostly) but indicate old-gen is filling.
- If concurrent cycles run constantly, you're near capacity.

### Common patterns and their meaning

**Frequent young GCs, short pauses, heap returns low** → healthy. Memory pressure is fine; this is normal allocation churn.

**Young GCs with growing pauses** → either young-gen too small (resize with `-XX:G1NewSizePercent`), or objects aren't dying young (check allocation patterns — maybe a hot allocator).

**Full GC** (`Pause Full (G1 Compaction Pause)`) → serious. G1 should avoid full GCs. Causes:
- Old-gen filled before concurrent cycle could keep up (heap too small).
- Humongous allocations (objects >50% of region size in G1).
- Memory leak.

**`System.gc()` pauses** → a library or code calls it. Find and remove:
```bash
grep -r "System.gc()\|Runtime.getRuntime().gc()" src/
# or use -XX:+DisableExplicitGC to ignore them
```

### Tools to interpret

**GCEasy** (gceasy.io) — upload the log, get pause frequency, throughput %, heap-occupancy graphs, and recommendations. The fastest way to analyze a log.

**GCViewer** — desktop tool, similar visualizations.

**JDK Mission Control** — for JFR recordings (related, more than GC).

**Manual** — `grep "Pause" gc.log | awk ...` for quick stats. The log is plain text; any scripting works.

### Reading a memory-pressure timeline

A healthy service:
```
... 10:00 young 200M->40M, 30ms
... 10:01 young 220M->42M, 32ms
... 10:02 young 240M->45M, 35ms
... 10:03 concurrent cycle starts (old-gen rising but reclaimed)
... 10:04 young 250M->40M, 30ms       ← back to normal
```

A leaking service:
```
... 10:00 young 200M->180M, 30ms      ← after-GC occupancy rising!
... 10:30 young 250M->230M, 45ms
... 11:00 young 280M->260M, 60ms      ← pauses growing
... 11:30 full GC 300M->290M, 800ms   ← full GC, barely any reclaim
... 11:45 OOM
```

The rising "after GC" number is the leak signal — long before OOM.

### Sample production JVM args (full)

```
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
-Xlog:gc*:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=10,filesize=50M
```

### Review checklist

When analyzing GC logs:
- [ ] GC logging enabled in prod (`-Xlog:gc*`)?
- [ ] Pause duration within SLA?
- [ ] After-GC heap occupancy stable (not climbing = leak)?
- [ ] GC cause checked — any `System.gc()`?
- [ ] No full GCs (or understood why they happen)?
- [ ] Log uploaded to GCEasy for visualization?

### Context

- **Java 9+ unified logging** replaced the Java 8 `-XX:+PrintGCDetails` flags entirely. Don't use the old syntax on Java 17+.
- **Log volume**: ~1-10MB/hour for a typical service. Rotation (`filecount=10,filesize=50M`) keeps it bounded.
- **GC logs + Micrometer**: `jvm.gc.pause`, `jvm.gc.live.data.size` metrics expose the same info as time-series for dashboards. Pairs well with logs for forensics.
- **Cross-ref**: tuning in response to log findings in `jvm/jvm-gc-tuning.md`; OOM investigation in `jvm/jvm-oom-analysis.md`; container memory sizing in `spring-boot/sb-config-profiles.md`.
