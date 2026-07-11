---
title: equals and hashCode Contract
impact: MEDIUM
impactDescription: Broken equals/hashCode causes silent bugs in HashSet/HashMap — lost entries, wrong contains
tags: equals, hashcode, contract, record, entity
description: Keep equals/hashCode consistent and stable; treat value objects, generated-id JPA entities, proxies, and mutable persistence objects differently
---

## equals and hashCode Contract

The contract: if `a.equals(b)` then `a.hashCode() == b.hashCode()`, always and forever. Break it and `HashMap`/`HashSet` quietly lose your objects.

### Why it matters

- **HashMap uses hashCode to bucket, equals to find**. If two equal objects have different hashes, the map looks in the wrong bucket → `containsKey` returns false even though the key is "in" the map.
- **HashSet stores unique**. If `equals` changes after insertion (because it depends on a mutable field), `contains` returns false for a member that's literally in the set.
- **Symptoms are confusing** — works in tests, fails when objects are mutated between `put` and `get`.

### The contract

For any `a`, `b`, `c`:
1. **Reflexive**: `a.equals(a)` is true.
2. **Symmetric**: `a.equals(b)` ⟺ `b.equals(a)`.
3. **Transitive**: `a.equals(b)` and `b.equals(c)` ⟹ `a.equals(c)`.
4. **Consistent**: repeated calls return the same result (no randomness).
5. **`a.equals(null)` is false**.
6. **Hash invariant**: `a.equals(b)` ⟹ `a.hashCode() == b.hashCode()`.

### Correct — use record

The simplest fix: use `record`. Records auto-generate `equals`/`hashCode` over all components, and they're correct by construction.

```java
public record Money(BigDecimal amount, String currency) {}
// equals and hashCode already correct
```

### Correct — manual equals/hashCode for an immutable value type

Use IDE generation or `Objects.equals`/`Objects.hash`. Pick the fields once and stick with them:

```java
public final class OrderNumber {
    private final String value;

    public OrderNumber(String value) {
        this.value = Objects.requireNonNull(value);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof OrderNumber other)) return false;
        return value.equals(other.value);
    }

    @Override
    public int hashCode() {
        return value.hashCode();
    }
}
```

### Critical — don't include mutable fields in hashCode

If you put an object in a `HashSet` and then mutate a hashCode-relevant field, the set can no longer find it:

```java
Set<Order> set = new HashSet<>();
Order o = new Order();
o.setOrderNo("A1");
set.add(o);
o.setOrderNo("A2");                                // ❌ hashCode changed
set.contains(o);                                   // false! even though o is in the set
```

**Rule**: fields used by `equals`/`hashCode` must be **effectively immutable while the object is in a hash-based collection**.

### Persistence entities — choose equality deliberately

Lombok `@Data` on an `@Entity`/`@TableName` is dangerous:

- Includes lazy proxies/associations → triggers DB hits on `equals`.
- Includes the `id`, which is **null before persist** → two distinct unsaved instances compare equal (both have null id), breaking `Set`/`Map`.

There is no single equality implementation that fits generated IDs, assigned IDs, natural keys, detached instances, and Hibernate proxies. Prefer an immutable natural key when one exists. If a JPA/Hibernate entity must use a generated database ID, use a null-id guard, a stable hash, and a proxy-aware type check:

```java
@Entity                                          // or @TableName for MP
public class Order {
    @Id @GeneratedValue
    private Long id;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || Hibernate.getClass(this) != Hibernate.getClass(o)) return false;
        Order other = (Order) o;
        return id != null && id.equals(other.id);
    }

    @Override
    public int hashCode() {
        return Hibernate.getClass(this).hashCode();  // stable and proxy-aware
    }
}
```

Why the hash must not use a generated ID:
- The id is null pre-persist, then assigned. If hashCode changes, the entity "disappears" from any HashSet it was added to before saving.
- A class-stable hash trades hash distribution for lifecycle stability while preserving the contract for equal persisted entities.

For MyBatis/MyBatis-Plus entities without ORM proxies, reference identity (`Object.equals`) is often safest unless the domain requires value or ID equality. Do not add Lombok `@Data` merely for convenience: mutable fields still make hash-based collection behavior unstable.

### Incorrect — `@Data` on entity

```java
@Data                                              // ❌ on @Entity
@Entity
public class Order {
    @Id private Long id;
    @OneToMany Set<OrderItem> items;               // lazy proxy — equals triggers SQL
    private String orderNo;
}
```
Comparing entities can initialize lazy associations and trigger unexpected SQL. The exact query count depends on proxy state and collection operations; treat any equality-triggered I/O as a design bug.

### Incorrect — `instanceof` without null-check pattern

```java
@Override
public boolean equals(Object o) {
    if (o instanceof Order) {                      // ❌ doesn't handle o being a subtype or null safely
        Order other = (Order) o;
        return id == other.id;                     // also: Long autoboxing == may compare references
    }
    return false;
}
```
Use the pattern variable form: `if (!(o instanceof Order other)) return false;` — null-safe and avoids the cast.

### Incorrect — comparing Long with `==`

```java
// ❌ Long is autoboxed; == compares object references for values outside -128..127 cache
return this.id == other.id;

// ✅
return Objects.equals(this.id, other.id);          // or this.id.equals(other.id) with null guard
```

### Review checklist

- [ ] Class with mutable fields that participates in `equals`/`hashCode`?
- [ ] `@Data`/generated equality on a JPA entity or mutable MyBatis-Plus entity?
- [ ] Long/Integer fields compared with `==` instead of `.equals`/`Objects.equals`?
- [ ] hashCode includes the `id` of an entity (changes after persist)?
- [ ] Two entities with all-equal fields except `id` — do they compare equal? (Should they?)
- [ ] `equals` doesn't handle `null` or different types?
- [ ] hashCode and equals use different fields (contract violation)?

### Context

- **Prefer `record`** for value types/DTOs — eliminates this whole category of bug.
- **Business-key equality**: if two Orders with the same `orderNo` should be equal regardless of database identity, use that key only when it is immutable and uniqueness is enforced.
- **`Objects.equals(a, b)`** is null-safe: returns true if both null, false if only one null, otherwise `a.equals(b)`. Always prefer it over `.equals` with manual null checks.
- **Cross-ref**: entity equality is detailed in `spring-boot/sb-jpa-repository.md` and `spring-boot/sb-mybatis-plus.md`; DTO-as-record in `spring-boot/sb-project-structure.md`.
