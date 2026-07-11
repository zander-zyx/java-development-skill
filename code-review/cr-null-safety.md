---
title: Null Safety and Optional
impact: HIGH
impactDescription: Ambiguous null contracts cause runtime failures and compatibility bugs; explicit contracts make absence and invalid input reviewable
tags: null, npe, optional, nullable, null-check
description: Make null contracts explicit; prefer Optional for ordinary absence when compatible, empty collections for no results, and project-standard nullability annotations
---

## Null Safety and Optional

Null handling is an API-design decision, not a mechanical rewrite. Preserve existing public contracts, then make absence, invalid input, and failure distinguishable with the project's established annotations and types.

### Why it matters

- **NPE is a runtime error** — silent in compilation, blows up in prod.
- **Null is ambiguous** — it can mean "no value", "not initialized", "error", or "not applicable". All four look identical.
- **Defensive null checks everywhere** make code ugly; the alternative (a no-nulls discipline) makes code clean and NPE-free.

### The rules

1. **Prefer `Optional` for new return types that model ordinary absence**, but do not break an existing public signature merely to introduce it.
2. **Prefer empty collections/arrays for “no results”** when the API contract permits it.
3. **Use one project-standard nullability system** (`org.jspecify.annotations`, Spring annotations, JetBrains annotations, Checker Framework, or the repository's existing choice).
4. **Reject invalid required inputs at the boundary** and preserve the documented exception type/message contract.
5. **Avoid ambiguous `null` arguments**; use overloads, named request objects, or an explicitly documented nullable parameter.

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

Spring projects may use `org.springframework.lang` annotations; newer codebases increasingly use JSpecify. Follow the existing repository because mixing annotation families weakens tooling and can create conflicting defaults.

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
// Usually avoid: many serializers/frameworks do not treat Optional fields as ordinary data
private Optional<User> currentUser;
```
Use `@Nullable User currentUser` instead.

**Optional as parameter**:
```java
// ❌ caller forced to wrap; no benefit over @Nullable
public void update(Optional<Order> order) { ... }
```
Prefer an overload or request type. A nullable parameter is acceptable when the repository already documents and checks that contract.

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
For a new API, return `Optional<Order>` or throw a domain exception when absence is exceptional. For an existing API, preserve source/binary behavior unless the compatibility change is requested and tested.

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

- [ ] Method's nullable return is undocumented or inconsistent with sibling APIs?
- [ ] `Optional` used as a field type or method parameter?
- [ ] `.get()` called on an Optional without an `isPresent`/`orElse` guard?
- [ ] Field/param can be null but isn't annotated `@Nullable`?
- [ ] `null` passed as an argument explicitly?
- [ ] `Map.get(k) != null` used where `containsKey` is meant?
- [ ] Collection/array return that could be null instead of empty?

### Context

- **`Optional` trade-off**: it may allocate and does not fit every serialization/framework boundary. Avoid it in measured hot loops and framework-managed fields unless support is explicit.
- **Checked exceptions vs Optional**: for "expected absence" use `Optional`; for "exceptional failure" throw. Don't return `Optional.empty()` for an error the caller must distinguish from a normal empty case.
- **JDK patterns**: `Objects.requireNonNull(obj, msg)` validates non-null at the top of a method and throws NPE with a clear message — use it for `@NonNull` params.
- **Cross-ref**: record validation interacts with DTO patterns in `spring-boot/sb-project-structure.md`; Optional return from JPA/MP repositories in `spring-boot/sb-jpa-repository.md` / `spring-boot/sb-mybatis-plus.md`.
