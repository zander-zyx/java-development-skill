---
title: JPA and Hibernate Best Practices
impact: HIGH
impactDescription: Prevents N+1 queries, lazy-loading exceptions, broken transactions, and bad equals/hashCode
tags: jpa, hibernate, n-plus-1, transactional, lazy-loading, uuid, entity
description: Avoid N+1 with JOIN FETCH/EntityGraph, scope @Transactional at service layer, disable open-in-view, use entity-aware equals
---

## JPA and Hibernate Best Practices

The four most common JPA disasters — N+1 queries, `LazyInitializationException`, broken transactions, and `equals`/`hashCode` that breaks on managed entities — are all preventable with a few consistent rules.

### Why it matters

- **N+1**: fetching 100 orders and their items fires 101 queries. In prod under load this kills the DB.
- **LazyInitializationException**: closing the session then touching a lazy collection throws. Often surfaces as "it works in dev, 500s in prod" because dev runs serially.
- **Silent no-op transactions**: a missing or mis-scoped `@Transactional` means writes don't persist (or worse, run in autocommit, half-persisting).
- **Broken equality**: Lombok `@Data` on an entity generates `equals` based on all fields — for a lazy proxy this triggers DB hits and for new entities (null id) two distinct instances compare equal, breaking `Set` semantics.

### Disable Open-InnoDB in View

`spring.jpa.open-in-view` defaults to `true` but should be `false`. With it on, the Hibernate session stays open for the entire HTTP request, silently masking lazy-loading problems in dev that explode as `LazyInitializationException` once you optimize.

```yaml
spring:
  jpa:
    open-in-view: false
```

Then handle lazy associations explicitly (see N+1 below).

### Prevent N+1 queries

Scenario: `Order` has a lazy `@OneToMany List<OrderItem>`.

Naïve (N+1):

```java
// ❌ for N orders this fires N+1 SELECTs
List<Order> orders = orderRepository.findAll();
for (Order o : orders) {
    o.getItems().size();  // triggers a SELECT per order
}
```

**Option 1 — JOIN FETCH** (JPQL):

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("SELECT DISTINCT o FROM Order o LEFT JOIN FETCH o.items")
    List<Order> findAllWithItems();
}
```

**Option 2 — EntityGraph** (preferred for reuse, no JPQL change):

```java
@Entity
@NamedEntityGraph(
    name = "Order.withItems",
    attributeNodes = @NamedAttributeNode("items")
)
public class Order { ... }

public interface OrderRepository extends JpaRepository<Order, Long> {
    @EntityGraph(value = "Order.withItems")
    List<Order> findAll();
}
```

**Option 3 — split into two queries** when you need pagination (JOIN FETCH breaks pagination on the root):

```java
// fetch page of orders, then bulk-fetch items for those ids in one query
List<Order> orders = orderRepository.findPage(pageRequest);
Set<Long> ids = orders.stream().map(Order::getId).collect(toSet());
Map<Long, List<OrderItem>> itemsByOrder = itemRepo.findByOrderIdIn(ids)
    .stream().collect(groupingBy(OrderItem::getOrderId));
// assemble in memory
```

**Rule of thumb**: any time you cross a `@OneToMany` or `@ManyToMany` in a list operation, decide up front: fetch-join it, graph it, or split it. Never iterate + touch.

### @Transactional placement

- **Service layer**: scope transactions here. A service method is the unit of business consistency.
- **Never on controllers**: too wide — holds DB connection across HTTP client calls.
- **Never on read-only queries unless needed**: `@Transactional(readOnly = true)` can help the DB optimize and prevents accidental writes.

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryClient inventoryClient;

    @Transactional                              // default read-write
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepository.save(buildOrder(req));
        inventoryClient.decrement(req.items()); // same tx as save
        return order;
    }

    @Transactional(readOnly = true)
    public Optional<Order> findOrder(Long id) {
        return orderRepository.findById(id);
    }
}
```

**Reversed transaction gotcha** — if `placeOrder` calls a *private* method annotated `@Transactional`, the annotation is **ignored** (Spring AOP is proxy-based). Self-invocation bypasses the proxy. Either call through another bean or move the boundary.

**Checked exception gotcha** — `@Transactional` only rolls back on `RuntimeException` (and `Error`) by default. A method that throws `IOException` will **commit**. Add `rollbackFor = Exception.class` if you throw checked exceptions:

```java
@Transactional(rollbackFor = Exception.class)
public void importCsv(Path p) throws IOException { ... }
```

### equals/hashCode for entities

Lombok `@Data` on `@Entity` is dangerous. It generates `equals` over every field including lazy collections (DB hit on every comparison) and the `id` (null for new entities → all unsaved instances "equal").

**Use the id-based equality with a null-id guard**:

```java
@Entity
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
        return getClass().hashCode();    // stable across entity lifecycle; see Context
    }
}
```

Why `getClass().hashCode()` rather than `Objects.hash(id)`: the id is null pre-persist and assigned post-persist; if hashCode changes, the entity is lost from any `HashSet`/`HashMap` it was put in before saving. A class-based hashCode is stable. This breaks the `equals`/`hashCode` contract *within a single persisted-vs-not comparison*, which is acceptable because two managed entities with the same id are the same row. (See `code-review/cr-equals-hashcode.md` for the general contract.)

Better: prefer records for value types and keep `@Entity` classes hand-rolled.

### Hibernate 6 (Spring Boot 3.x) — UUID and GeneratedValue

Hibernate 6 changes two things you'll trip on during 2.x → 3.x migration:

1. **`@GeneratedValue(strategy = GenerationType.AUTO)` now resolves to IDENTITY** (was Sequence/Table). Existing sequences may be ignored — verify your `@SequenceGenerator` is still used, or switch to an explicit strategy.

2. **Native UUID support** — you can now use UUIDs as natural keys cleanly:

```java
@Entity
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)   // Hibernate 6 / JPA 3.1
    @Column(columnDefinition = "uuid")
    private UUID id;
}
```

Watch the **column DDL**: UUID often changed from `binary(16)` to `varchar(36)` across versions, which can break existing schemas. Validate with `ddl-auto=validate` on staging first.

### Context

- **open-in-view**: Spring sets it `true` by default for "convenience" but logs a warning. Turn it off and fix the laziness explicitly — see the N+1 rules above.
- **DTO projections**: for read-heavy endpoints, project straight to a DTO via interface/record projection instead of loading entities — avoids lazy issues entirely.
- **Cross-ref**: `@Transactional` self-invocation is a variant of the proxy pitfall in `code-review/cr-concurrency.md`; entity equality expanded in `code-review/cr-equals-hashcode.md`; 2.x→3.x migration including Hibernate changes in `spring-boot/sb-migration-2-to-3.md`.
