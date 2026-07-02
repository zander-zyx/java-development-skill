---
title: High CPU Troubleshooting
impact: HIGH
impactDescription: Pinpoint the hot thread with top -Hp + jstack, then sample with async-profiler for the hot method
tags: cpu, high-cpu, top-hp, jstack, async-profiler, flamegraph
description: Find the hot OS thread with top -Hp, map to Java thread via nid in jstack, then profile with async-profiler
alwaysApply: true
---

## High CPU Troubleshooting

When CPU pegs at 100% (or the container is throttled), the cause is one hot thread — usually an infinite loop, a regex catastrophic backtracking, or a hot algorithm. Find that thread, then find the hot method.

### Why it matters

- **High CPU = either real work or a bug** — you need to distinguish. A spike during traffic is expected; a spike at idle is a bug.
- **Averages hide culprits** — a single spinning thread can peg one core while the app looks "only 12% CPU" on a 8-core box. Per-thread breakdown matters.
- **The fix is specific** — a generic "tune the JVM" never helps. You need the stack of the spinning thread.

### Step 1: Confirm it's the Java process

```bash
top -c
# or
ps -e -o pid,pcpu,comm --sort -pcpu | head
```

Identify the PID of the Java process consuming CPU. Confirm it's the JVM, not a co-located process.

### Step 2: Find the hot thread within the JVM

```bash
# Linux: top per-thread, sorted by CPU
top -H -p <pid>
```

`-H` shows threads (OS-level) instead of processes. Sort by CPU; note the **TID** (thread ID) of the hottest one.

Convert the decimal TID to hex — that's the `nid` (native id) in the thread dump:

```bash
printf "%x\n" <tid>          # e.g. 12345 → 0x3039
```

### Step 3: Capture a thread dump and find the hot thread

```bash
jstack <pid> > t1.txt; sleep 5; jstack <pid> > t2.txt
```

Find the thread whose `nid=0x3039`:

```
"http-nio-8080-exec-7" #58 daemon prio=5 ... runnable
   java.lang.Thread.State: RUNNABLE
        at com.acme.Slugify.slugify(Slugify.java:42)        ← matches in both t1 and t2
        at com.acme.PostService.create(PostService.java:80)
```

If the same stack appears in both dumps, that thread is stuck in `Slugify.slugify`. If the top frame changes, it's busy legitimate work — sample with a profiler instead.

### Step 4: Profile with async-profiler (recommended)

`async-profiler` samples CPU at low overhead and produces a flame graph:

```bash
# 30-second CPU sample, output flame graph HTML
./profiler.sh -d 30 -f cpu.html <pid>
```

Open `cpu.html` in a browser. The widest blocks at the top are where CPU is spent:

```
|-- java.lang.Thread.run
    |-- com.acme.Worker.process
        |-- com.acme.Slugify.slugify        ← wide = hot
            |-- java.util.regex.Pattern.matcher
                |-- java.util.regex.Pattern$Curly.match    ← the regex engine
```

This points straight at the hot method. async-profiler is non-intrusive (no JVMTI agent overhead like JFR-on-JDK-Mission-Control sometimes has, safe for prod).

Alternatives:
- **JDK Flight Recorder (JFR)** — built into the JDK, low overhead, captures CPU + allocation + IO.
  ```bash
  jcmd <pid> JFR.start duration=60s filename=/tmp/recording.jfr
  # then open recording.jfr in JDK Mission Control
  ```
- **Arthas (Alibaba)** — popular in China; `profiler start` / `profiler stop --format html`.

### Step 5: Common causes of high CPU

**Infinite loop / spin**:
```java
// ❌ condition never becomes false
while (!queue.isEmpty()) { }   // busy-wait without sleep → pegs a core
```

**Regex catastrophic backtracking**:
```java
// ❌ on input "aaaaaaaaaaaaaaaaaaaaaaaaaaab"
Pattern.matches("(a+)+b", input);   // exponential
```
Fix: anchor patterns, avoid nested quantifiers, set a matching timeout, or use a non-backtracking engine (RE2J).

**Inefficient algorithm in a hot path**:
- O(n²) loop that was fine at 100 items, kills at 10k.
- `String.concat` in a loop → quadratic; use `StringBuilder`.
- Autoboxing in a hot loop (`Integer` arithmetic) → allocation pressure.

**Unintended serialization / reflection in a hot path**:
- Jackson `ObjectMapper.readValue` called per-request — but with `readValue(slowJson, Object.class)` triggering type discovery each call.

**GC thrashing** (looks like CPU): if the GC log shows frequent collections and CPU is high, the GC is the consumer — see `jvm-gc-tuning.md`.

**Lock spinning**: in modern JDKs, contended locks spin briefly before parking — sustained contention can show as CPU. The thread state is `RUNNABLE` but the stack shows monitor operations. See `jvm-thread-dump.md`.

### Step 6: Verify the fix

After fixing:
- CPU returns to baseline at the same traffic level.
- p99 latency drops (a hot CPU core was delaying everything sharing it).
- No regression under load test.

### Review checklist

When investigating high CPU:
- [ ] Confirmed it's the Java process (not a co-located one)?
- [ ] Per-thread CPU checked (`top -H`)? A single hot thread can hide in averages.
- [ ] Hot thread's TID converted to hex and located in `jstack`?
- [ ] Same stack in two dumps 5-10s apart (indicates a spin)?
- [ ] async-profiler / JFR flame graph captured?
- [ ] Common causes checked: infinite loop, regex backtracking, hot algorithm, GC thrashing?
- [ ] Distinguished "real work CPU" (expected under load) from "idle CPU" (a bug)?

### Context

- **Container CPU limits**: K8s CPU limits throttle via CFS; the JVM sees 100% CPU but is throttled. Check `container_cpu_cfs_throttled_seconds_total` — if high, the limit is too low, not the app misbehaving.
- **async-profiler permissions**: needs `kernel.perf_event_paranoid <= 1` on Linux for perf-events mode; otherwise runs in bytecode-instrumentation mode (still works, less accurate).
- **Cross-ref**: thread dump mechanics in `jvm-thread-dump.md`; GC-as-CPU-cause in `jvm-gc-tuning.md`; regex backtracking relates to the resource-review in `code-review/cr-anti-patterns.md`.
