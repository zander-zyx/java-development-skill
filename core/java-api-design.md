---
title: Java API Design and Compatibility
impact: HIGH
impactDescription: Public API changes can silently break downstream modules, serialized data, binary compatibility, or client contracts
tags: java, api-design, compatibility, generics, records, serialization
description: Design and modify Java APIs conservatively by preserving source, binary, serialization, and behavioral compatibility unless a breaking change is requested
---

## Java API Design and Compatibility

Use this when changing public/protected classes, interfaces, method signatures, DTOs, exceptions, annotations, or library modules consumed by other code.

### Why it matters

Java APIs are contracts. A change that compiles locally can still break downstream callers, reflection, serialization, frameworks, generated code, or binary-compatible consumers that do not recompile immediately.

### First classify the API

1. **Visibility**: public/protected API, package-private internal, test helper, or private implementation.
2. **Consumers**: same module, multi-module repo, external library clients, reflection/framework, JSON/XML clients.
3. **Compatibility type**: source, binary, serialization, database/schema, wire format, or behavioral.
4. **Java level**: whether `record`, sealed classes, pattern matching, or newer APIs are allowed.

### Correct

Prefer additive changes for stable APIs:

```java
public interface OrderClient {
    Order getOrder(String id);

    default Optional<Order> findOrder(String id) {
        return Optional.ofNullable(getOrder(id));
    }
}
```

For DTOs, preserve serialized field names unless the API version changes:

```java
public record OrderResponse(
        String id,
        String status,
        BigDecimal amount
) {}
```

### Rules

- Do not remove or rename public methods, fields, enum constants, JSON fields, or exception types without explicit breaking-change approval.
- Avoid changing parameter meaning while keeping the same signature; that is a behavioral breaking change.
- Prefer returning interfaces (`List`, `Map`) while documenting mutability; do not expose internal mutable collections.
- Use `Optional` mainly for return values, not fields, parameters, or serialized DTO properties unless the project already does.
- Preserve generic type safety; do not introduce raw types to silence compiler errors.
- For libraries, avoid adding heavyweight framework dependencies to core modules.
- When using `record`, verify framework serialization/deserialization and Java target compatibility.

### When NOT to use

- Private implementation details can be refactored more freely when tests cover behavior.
- Internal APIs in a single module can change when all callers are updated in the same change.
- Breaking changes are acceptable when the user explicitly requests a major-version migration and the impact is documented.

### Verification

```bash
mvn -q test
./gradlew test
jdeps --multi-release 17 path/to/artifact.jar
```

For published libraries, also run downstream sample tests or binary compatibility checks when available.

### Context

- Cross-ref project classification in `core/java-general-development.md`.
- Cross-ref null contracts in `code-review/cr-null-safety.md`.
- Cross-ref equality contracts in `code-review/cr-equals-hashcode.md`.
