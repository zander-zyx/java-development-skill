---
title: Thread Dump and Deadlock Detection
impact: HIGH
impactDescription: A thread dump reveals hangs, deadlocks, and thread leaks — the diagnostic for "app is stuck"
tags: thread-dump, deadlock, jstack, jcmd, blocked, hung
description: Capture multiple thread dumps 10s apart; look for BLOCKED threads and deadlock detection; count threads for leaks
alwaysApply: true
---

## Thread Dump and Deadlock Detection

When the app hangs, requests time out, or a thread count climbs — the thread dump tells you what every thread is doing right now. Multiple dumps seconds apart reveal what's stuck vs. just busy.

### Why it matters

- **Hangs have many causes**: deadlock, all threads blocked on a lock, all DB connections busy, infinite loop on a hot thread, or a slow downstream service. The thread dump distinguishes them.
- **One snapshot can mislead**: a thread in `RUNNABLE` at capture might be doing real work or might be spinning — only comparing snapshots reveals the difference.
- **Deadlock detection is automatic** — the JVM prints it; you just need to look.

### Step 1: Capture multiple thread dumps

```bash
# jstack (HotSpot)
jstack <pid> > t1.txt; sleep 10; jstack <pid> > t2.txt; sleep 10; jstack <pid> > t3.txt

# jcmd (preferred JDK 8+)
jcmd <pid> Thread.print > t1.txt

# Force a dump even if the JVM is unresponsive (HotSpot)
kill -3 <pid>                                 # prints to the JVM's stdout
# or: jstack -F <pid>                        # forced, for hung JVMs
```

Three dumps ~10 seconds apart. Threads that show **the same stack** in all three dumps are stuck (or sleeping/waiting deliberately — read the state).

### Step 2: Read thread states

| State | Meaning | Action |
|-------|---------|--------|
| `RUNNABLE` | Running or ready to run (may be doing IO, blocked in native) | Check if it's CPU-spinning (same stack over time) |
| `BLOCKED` | Waiting to acquire a monitor lock held by another thread | Likely contended lock or deadlock |
| `WAITING` | Waiting indefinitely (`Object.wait()`, `Thread.join()`, `LockSupport.park`) | Often normal (pool threads idle) |
| `TIMED_WAITING` | Waiting with timeout (`Thread.sleep`, `wait(ms)`) | Usually normal |
| `NEW` / `TERMINATED` | Not started / finished | — |

### Step 3: Check for deadlock (automatic)

The JVM detects monitor deadlocks automatically. `jstack` prints a section at the bottom:

```
Found one Java-level deadlock:
=============================
"Thread-1":
  waiting to lock monitor 0x... (object 0x..., a java.lang.Object),
  which is held by "Thread-2"
"Thread-2":
  waiting to lock monitor 0x... (object 0x..., a java.lang.Object),
  which is held by "Thread-1"

Java stack information for the threads listed above:
===================================================
"Thread-1":
    at com.acme.OrderService.reserve(OrderService.java:42)
    - waiting to lock <0x...> (a java.lang.Object)
    ...
```

The cycle (`Thread-1 → Thread-2 → Thread-1`) is the deadlock. Fix by acquiring locks in a consistent order — see `code-review/cr-concurrency.md`.

For `java.util.concurrent.locks.Lock` deadlocks (ReentrantLock, etc.), `jstack` may not auto-detect — read the stacks manually: threads in `WAITING (on parking)` waiting on the same lock abstraction.

### Step 4: Identify blocked threads

Filter the dump for `BLOCKED`:

```bash
grep -A 5 "BLOCKED" t1.txt
```

If many threads are BLOCKED on the same monitor, that's severe lock contention. Common causes:
- A coarse-grained `synchronized` block over a long operation (DB call, HTTP).
- A "hot" lock on a frequently-updated cache.

### Step 5: Identify stuck threads (same stack over time)

Compare the three dumps. A thread whose top frame is identical across all three is stuck:

```
"http-nio-8080-exec-5" #45 daemon prio=5 ... waiting on condition
   java.lang.Thread.State: WAITING (parking)
        at jdk.internal.misc.Unsafe.park(Native Method)
        - parking to wait for  <0x...> (a java.util.concurrent.CountDownLatch$Sync)
        at com.acme.OrderService.waitForInit(OrderService.java:80)   ← stuck here in all 3 dumps
```

If `waitForInit` never completes (init failed silently), this thread is permanently parked — leak.

### Step 6: Thread count + leak detection

```bash
# count threads
jcmd <pid> Thread.print | grep "java.lang.Thread.State" | wc -l
# or
jstack <pid> | grep "^\"" | wc -l
```

Compare to the thread pool's expected max. If the count climbs over time (capture hours apart), there's a thread leak:
- `new Thread(...)` started but never finishing (infinite loop, blocked forever).
- An `ExecutorService` whose tasks block indefinitely.
- A connection pool whose acquire threads pile up.

### Step 7: Common patterns

**All HTTP threads WAITING on a DB connection** — HikariCP pool exhausted. Threads show:
```
at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:...)
```
Fix: investigate slow queries / unclosed connections, or tune pool size.

**One thread RUNNABLE with the same stack forever** — infinite loop or hot spin. Same stack across dumps = spinning. Sample CPU (see `jvm/jvm-cpu-high.md`) to confirm.

**Many threads BLOCKED on one monitor** — coarse lock contention. The "owner" thread's stack tells you what it's doing while holding the lock.

**Threads stuck in `Object.wait()` on a custom class** — usually a hand-rolled producer/consumer with a missing `notify`.

### Step 8: Tools beyond jstack

- **fastthread.io** — online analyzer, paste the dump, get a visualization.
- **JDK Mission Control (jcmd + JFR)** — records over time, not snapshots.
- **VisualVM** — live thread view + on-demand dumps.
- **Arthas (Alibaba)** — popular in China for live diagnosis, includes `thread` command for dumps and deadlock detection.

### Review checklist

When investigating a hang:
- [ ] At least 3 thread dumps captured ~10s apart?
- [ ] `Found one Java-level deadlock` section read?
- [ ] `BLOCKED` threads counted and grouped by the monitor they wait on?
- [ ] Same-stack threads across all dumps identified (stuck)?
- [ ] Thread count vs pool maximum compared?
- [ ] Connection-pool-wait patterns checked (HikariCP, etc.)?

### Context

- **`jstack -F`**: forces a dump on a hung JVM via `SIGQUIT`-equivalent. Use when normal `jstack` times out.
- **Native threads**: a JVM thread maps to an OS thread (carrier thread in virtual-thread model). Native hangs (NIO, JNI) may not show useful Java frames — pair with OS-level tools (`perf`, `strace`).
- **Virtual threads (Java 21+)**: `jcmd <pid> Thread.print` includes virtual threads; they're cheap so a high count is normal. Look for *carrier thread* pinning instead.
- **Cross-ref**: high CPU often co-occurs with hangs — `jvm/jvm-cpu-high.md`; resource/thread leaks that lead here in `code-review/cr-resource-leak.md` and `code-review/cr-concurrency.md`.
