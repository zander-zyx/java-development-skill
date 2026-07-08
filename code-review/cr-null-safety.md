---
title: Null Safety and Optional
impact: HIGH
impactDescription: NPE is the #1 Java runtime exception; disciplined Optional + annotations prevent it
tags: null, npe, optional, nullable, null-check
description: Use Optional only as a return type; annotate fields/params with @Nullable; never pass null into APIs
alwaysApply: true
---

## Null Safety and Optional

`NullPointerException` is the most-thrown exception in Java. The fixes are: prefer `Optional` as a return type, annotate nullability, and avoid passing `null` as input.

### Why it matters

- **NPE is a runtime error** — silent in compilation, blows up in prod.
- **Null is ambiguous** — it can mean "no value", "not initialized", "error", or "not applicable". All four look identical.
- **Defensive null checks everywhere** make code ugly; the alternative (a no-nulls discipline) makes code clean and NPE-free.

### The rules

1. **`Optional` is for return types only**. Don't store it in fields, don't accept it as a parameter.
2. **Never return `null`** from a method that might not have a result — return `Optional`.
3. **Annotate** nullable params/fields with `@Nullable`; treat unannotated as non-null.
4. **Don't pass `null`** as an argument — overload or use a sentinel object.

### Correct — Optional as return type

```java
public Optional<Order> findById(Long id) {
    return Optional.ofNullable(mapper.selectById(id));
}

// caller forced to handle absence
orderRepo.findById(id)
    .map(this::toResponse)
    .orElseThrow(() -> new OrderNotFoundException(id));
```

### Correct — annotations

```java
import org.springframework.lang.Nullable;
import org.springframework.lang.NonNull;

public class OrderService {
    public Order create(@NonNull OrderRequest req, @Nullable String coupon) {
        // req is guaranteed non-null (caller should not pass null)
        // coupon may be null — handle explicitly
        if (coupon != null) { applyCoupon(coupon); }
        // ...
    }
}
```

Spring's `@Nullable`/`@NonNull` are the most common in Spring apps (in `org.springframework.lang`). IntelliJ/IDEA uses these for inspection. Alternatives: JSR-305 `javax.annotation.*`, JetBrains `org.jetbrains.annotations.*`, or Jakarta's `jakarta.annotation.*`.

### Correct — empty collections, not null

```java
// ✅ empty list — caller iterates safely
public List<Order> findExpired() {
    var found = mapper.selectList(...);
    return found != null ? found : List.of();
}

// ❌ null list — caller must null-check before iterating
public List<Order> badFindExpired() {
    return null;                                   // every caller needs: if (list != null) ...
}
```

Use `Collections.emptyList()` or `List.of()` (immutable). Prefer immutability.

### Incorrect — Optional misuse

**Storing Optional in a field**:
```java
// ❌ Optional is not serializable, adds overhead, designed for return values
private Optional<User> currentUser;
```
Use `@Nullable User currentUser` instead.

**Optional as parameter**:
```java
// ❌ caller forced to wrap; no benefit over @Nullable
public void update(Optional<Order> order) { ... }
```
Use `@Nullable Order order` or overload: `update()` + `update(Order)`.

**Calling `.get()` without checking**:
```java
// ❌ throws NoSuchElementException — the very NPE we tried to prevent
Order o = orderRepo.findById(id).get();
```
Use `.orElseThrow(...)`, `.orElse(default)`, or `.ifPresent(...)`.

**Chaining `.map` then `.get`**:
```java
// ❌ still throws if empty
String name = opt.map(User::getName).get();
```
Use `.orElse(...)` / `.orElseThrow()`.

### Incorrect — returning null

```java
// ❌ caller has no signal this can be null
public Order find(Long id) {
    Order o = mapper.selectById(id);
    return o;                                      // NPE risk for caller
}
```
Return `Optional<Order>` or throw a domain exception (`orElseThrow`). Reserve null returns for very legacy APIs and document loudly.

### Incorrect — passing null

```java
// ❌ ambiguous: is null "no filter" or a bug?
orderService.search(null, "PAID");

// ✅ overload or sentinel
orderService.searchAll("PAID");
orderService.searchByUser(userId, "PAID");
```

### Correct — null-hostile collections

`Map.get(key)` returns null both when the key maps to null and when the key is absent. Disambiguate:

```java
if (map.containsKey(key)) { ... }                  // ✅ explicit
// vs
if (map.get(key) != null) { ... }                  // ❌ wrong if the value is genuinely null
```

Or use `Map.getOrDefault(key, defaultValue)`.

### Avoid null arrays

If an API returns `Order[]`, returning `null` forces callers to null-check. Return an empty array: `new Order[0]` or `Order[]::new`.

### Modern Java — null-hostile types

- **`record`** — components can be null; validate in compact constructor.
- **`@NonNull`** on record components + validation in constructor gives you non-null by construction.

```java
public record OrderRequest(@NonNull String userId, @NonNull BigDecimal amount) {
    public OrderRequest {
        Objects.requireNonNull(userId, "userId");
        Objects.requireNonNull(amount, "amount");
    }
}
```

Now no `OrderRequest` instance can exist with null fields — the bug is impossible at the type level.

### Review checklist

- [ ] Method returns null where it could return `Optional` or empty collection?
- [ ] `Optional` used as a field type or method parameter?
- [ ] `.get()` called on an Optional without an `isPresent`/`orElse` guard?
- [ ] Field/param can be null but isn't annotated `@Nullable`?
- [ ] `null` passed as an argument explicitly?
- [ ] `Map.get(k) != null` used where `containsKey` is meant?
- [ ] Collection/array return that could be null instead of empty?

### Context

- **`Optional` performance**: it's an object allocation per call; fine for return types, inappropriate in hot inner loops or fields. Don't over-apply.
- **Checked exceptions vs Optional**: for "expected absence" use `Optional`; for "exceptional failure" throw. Don't return `Optional.empty()` for an error the caller must distinguish from a normal empty case.
- **JDK patterns**: `Objects.requireNonNull(obj, msg)` validates non-null at the top of a method and throws NPE with a clear message — use it for `@NonNull` params.
- **Cross-ref**: record validation interacts with DTO patterns in `spring-boot/sb-project-structure.md`; Optional return from JPA/MP repositories in `spring-boot/sb-jpa-repository.md` / `spring-boot/sb-mybatis-plus.md`.
