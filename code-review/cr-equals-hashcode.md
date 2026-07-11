---
title: equals and hashCode Contract
impact: MEDIUM
impactDescription: Broken equals/hashCode causes silent bugs in HashSet/HashMap — lost entries, wrong contains
tags: equals, hashcode, contract, record, entity
description: equals and hashCode must be consistent; never include mutable/derived fields; use id-based equality for JPA/MP entities
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

### Correct — manual equals/hashCode for mutable types

Use IDE generation or `Objects.equals`/`Objects.hash`. Pick the fields once and stick with them:

```java
public class Order {
    private Long id;
    private String orderNo;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Order other)) return false;
        return Objects.equals(id, other.id) && Objects.equals(orderNo, other.orderNo);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, orderNo);
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

**Rule**: hashCode/equals fields must be **effectively immutable after insertion into a hash-based collection**. For JPA/MP entities, use the id (assigned once) — see below.

### JPA/MP entities — id-based equality

Lombok `@Data` on an `@Entity`/`@TableName` is dangerous:

- Includes lazy proxies/associations → triggers DB hits on `equals`.
- Includes the `id`, which is **null before persist** → two distinct unsaved instances compare equal (both have null id), breaking `Set`/`Map`.

Use id-based equality with a null-id guard:

```java
@Entity                                          // or @TableName for MP
public class Order {
    @Id @GeneratedValue
    private Long id;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Order other)) return false;
        return id != null && id.equals(other.id);   // null id → never equal (distinct new entities)
    }

    @Override
    public int hashCode() {
        return getClass().hashCode();                // stable; doesn't depend on id
    }
}
```

Why `getClass().hashCode()` and not `Objects.hash(id)`:
- The id is null pre-persist, then assigned. If hashCode changes, the entity "disappears" from any HashSet it was added to before saving.
- A class-constant hashCode is stable across the lifecycle. This technically breaks the contract for two distinct unsaved entities, but unsaved entities shouldn't be in a Set anyway.

For MyBatis-Plus entities (no lazy proxy), the situation is simpler — `@Data` is generally safe — but the null-id issue still applies if you use entities in Sets pre-insert. Use the same pattern.

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
Comparing two Orders fires a SQL query for `items`. In a `HashSet<Order>` of 1000 orders, every `contains` is 1000 SQL roundtrips.

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
- [ ] `@Data` (Lombok) on a JPA `@Entity` or MyBatis-Plus `@TableName`?
- [ ] Long/Integer fields compared with `==` instead of `.equals`/`Objects.equals`?
- [ ] hashCode includes the `id` of an entity (changes after persist)?
- [ ] Two entities with all-equal fields except `id` — do they compare equal? (Should they?)
- [ ] `equals` doesn't handle `null` or different types?
- [ ] hashCode and equals use different fields (contract violation)?

### Context

- **Prefer `record`** for value types/DTOs — eliminates this whole category of bug.
- **Business-key equality**: if you want two Orders with the same `orderNo` to be equal regardless of id, use `orderNo` in equals/hashCode — but make `orderNo` immutable and unique.
- **`Objects.equals(a, b)`** is null-safe: returns true if both null, false if only one null, otherwise `a.equals(b)`. Always prefer it over `.equals` with manual null checks.
- **Cross-ref**: entity equality is detailed in `spring-boot/sb-jpa-repository.md` and `spring-boot/sb-mybatis-plus.md`; DTO-as-record in `spring-boot/sb-project-structure.md`.
