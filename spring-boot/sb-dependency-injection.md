---
title: Constructor Injection with Lombok Essentials
impact: HIGH
impactDescription: Prevents field-injection pitfalls, enables immutability and easy testing
tags: di, constructor-injection, lombok, beans, spring
description: Use constructor injection via final fields + @RequiredArgsConstructor; restrict Lombok to @RequiredArgsConstructor/@Slf4j/@Data
alwaysApply: true
---

## Constructor Injection with Lombok Essentials

Use constructor injection with `final` fields as the only injection style. Generate the constructor with Lombok `@RequiredArgsConstructor`. Restrict Lombok usage to a short allowlist.

### Why it matters

Field injection (`@Autowired` on a field) is widely discouraged by the Spring team and has real costs:

- **Hides dependencies** — a class with 10 `@Autowired` fields looks fine until you try to instantiate it; constructor injection makes the dependency surface visible at the call site.
- **Breaks immutability** — `@Autowired` fields cannot be `final`, so beans are mutable after construction.
- **Harder to test** — unit tests must use reflection (`ReflectionTestUtils`) or Spring context to inject mocks, instead of simply `new MyService(mockRepo)`.
- **Hides circular dependencies** — constructor injection fails fast at startup; field injection may let a cycle slip through until runtime.

### Correct

Use constructor injection via `@RequiredArgsConstructor` on `final` fields:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final PaymentClient paymentClient;
    private final Clock clock;  // inject Clock for testable time

    public Order placeOrder(OrderRequest request) {
        log.info("Placing order for user={}", request.userId());
        // ...
    }
}
```

For a class with a **single constructor**, Spring injects automatically — no need for `@Autowired` on the constructor at all. `@RequiredArgsConstructor` generates that single constructor over the `final` fields.

### Manual constructor (when you need to massage args)

If you need to transform an argument before assigning, write the constructor by hand and skip `@RequiredArgsConstructor` for that class:

```java
@Service
@Slf4j
public class PricingService {
    private final DiscountPolicy discountPolicy;

    public PricingService(DiscountProperties props) {
        this.discountPolicy = new DiscountPolicy(props.getRules());  // adapt raw config
    }
}
```

### Lombok allowlist

Use only these Lombok annotations in this skill:

| Annotation | Use for | Notes |
|------------|---------|-------|
| `@RequiredArgsConstructor` | Service/Component classes with final deps | The DI workhorse |
| `@Slf4j` | Any class that logs | Replaces `private static final Logger` boilerplate |
| `@Data` | JPA `@Entity` and mutable POJOs | Generates getters/setters/equals/hashCode/toString |
| `@Getter` / `@Setter` | When you don't want all of `@Data` | Prefer `record` for DTOs instead |

**Avoid**: `@AllArgsConstructor` (fights with Spring's single-constructor autowiring), `@Builder` on entities (hides required fields), `@NonNull` on fields (use Spring/JSR-305 annotations instead), `@SneakyThrows` (swallows checked exceptions silently).

### Prefer record for DTOs

For request/response DTOs and value objects, prefer a Java `record` over `@Data`:

```java
public record OrderRequest(String userId, List<OrderItem> items, String couponCode) {}
```

Records are immutable, auto-generate accessors/equals/hashCode/toString, and need no Lombok at all. Reserve `@Data` for JPA entities (which need mutable setters and no-arg constructor) or legacy mutable POJOs.

### Incorrect

Field injection — avoid:

```java
@Service
public class OrderService {
    @Autowired                          // ❌ field injection: untestable, mutable, hides deps
    private OrderRepository orderRepository;
    @Autowired
    private PaymentClient paymentClient;
}
```

Setter injection for required dependencies — avoid (it implies the bean works without them, which is false):

```java
@Service
public class OrderService {
    private OrderRepository orderRepository;

    @Autowired                          // ❌ makes a required dep look optional
    public void setOrderRepository(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }
}
```

Lombok abuse — avoid `@AllArgsConstructor` on beans Spring instantiates:

```java
@Service
@AllArgsConstructor      // ❌ generates ctor over ALL fields incl. non-final; clashes with DI intent
public class OrderService {
    private OrderRepository orderRepository;   // not even final
    private int retryCount = 3;
}
```

### Testing is now trivial

Because dependencies are constructor parameters, unit tests need no Spring context:

```java
@Test
void placesOrderThroughRepository() {
    var repo = mock(OrderRepository.class);
    var payment = mock(PaymentClient.class);
    var service = new OrderService(repo, payment, Clock.systemUTC());

    service.placeOrder(new OrderRequest("u1", List.of(), null));

    verify(repo).save(any(Order.class));
}
```

### Context

- **Single constructor + Spring 4.3+**: Spring auto-injects when there is exactly one constructor, even without `@Autowired`. `@RequiredArgsConstructor` produces exactly one, so this just works.
- **Circular dependencies**: SB 3.x fails startup on circular references by default (it was already discouraged in 2.x). If you hit one, the fix is usually to extract a third collaborator, not to re-enable field injection.
- **Lombok config**: To forbid field injection at compile time, add `lombok.copyableAnnotations += org.springframework.beans.factory.annotation.Qualifier` in `lombok.config` so qualifiers propagate onto the generated constructor params.
- **Cross-ref**: For JPA entity `@Data` caveats (the generated `equals`/`hashCode` can break lazy loading), see `spring-boot/sb-jpa-repository.md` and `code-review/cr-equals-hashcode.md`.
