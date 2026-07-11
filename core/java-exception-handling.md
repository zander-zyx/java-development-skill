---
title: Java Exception and Failure Handling
impact: HIGH
impactDescription: Poor exception handling hides root causes, breaks cancellation, corrupts transactions, or makes production incidents impossible to diagnose
tags: java, exceptions, error-handling, interrupt, logging, transactions
description: Handle Java failures by preserving causes, respecting interrupts, avoiding swallowed exceptions, and mapping errors at the correct boundary
---

## Java Exception and Failure Handling

Use this when adding or reviewing exception handling, retries, async code, transaction boundaries, CLI error output, or API error mapping.

### Why it matters

Incorrect exception handling often looks safe in tests but fails in production: root causes disappear, threads ignore cancellation, retries multiply side effects, and callers receive misleading errors.

### Correct

Preserve the cause and add useful context:

```java
try {
    return client.fetchOrder(orderId);
} catch (IOException e) {
    throw new OrderClientException("Failed to fetch order " + orderId, e);
}
```

Respect interruption:

```java
try {
    queue.put(event);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    throw new EventPublishException("Interrupted while publishing event", e);
}
```

### Rules

- Never swallow exceptions silently. If ignoring is intentional, document why and make the condition narrow.
- Do not log and rethrow at every layer; log at the boundary that can act on the failure.
- Preserve exception causes with constructor chaining.
- Respect `InterruptedException`: restore interrupt status or propagate it.
- Keep retry logic idempotent and bounded; add backoff for remote calls.
- Map exceptions at system boundaries: CLI exit codes, REST errors, messaging dead-letter policy, or batch job status.
- Do not catch broad `Exception`/`Throwable` unless implementing a true boundary or cleanup guard.

### When NOT to use

- Do not wrap exceptions just to change their type if it removes useful caller information.
- Do not convert checked exceptions to unchecked ones in library APIs without considering caller recovery.
- Do not add retries around non-idempotent writes unless the operation has idempotency keys or compensation.

### Verification

Add tests for failure paths, not only happy paths:

```bash
mvn -q -Dtest='*Exception*Test,*Failure*Test' test
./gradlew test --tests '*Exception*Test' --tests '*Failure*Test'
```

### Context

- Cross-ref resource cleanup in `code-review/cr-resource-leak.md`.
- Cross-ref REST error mapping in `spring-boot/sb-exception-handling.md` when Spring Boot is in scope.
- Cross-ref concurrency and interruption in `code-review/cr-concurrency.md`.
