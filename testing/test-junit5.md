---
title: JUnit 5 Patterns
impact: HIGH
impactDescription: JUnit 5 lifecycle, parameterized tests, and extensions unlock fast readable tests
tags: junit5, testing, lifecycle, parameterized, extension
description: Use JUnit 5 lifecycle (BeforeEach/All), parameterized tests for data-driven cases, extensions over inheritance
alwaysApply: true
---

## JUnit 5 Patterns

JUnit 5 (Jupiter) is the standard. Use its lifecycle hooks, parameterized tests, and extension model over hand-rolled setup and loops.

### Why it matters

- **Parameterized tests** replace boilerplate loops over test data — one method, many inputs, individual failures.
- **Lifecycle hooks** (`@BeforeEach`, `@BeforeAll`) give clean isolation; running tests in any order doesn't break anything.
- **Extensions** (`@ExtendWith`) replace the JUnit 4 runner model — composable, no single-runner limit.

### Lifecycle

```java
class OrderServiceTest {
    private OrderService service;

    @BeforeAll                                      // runs once before all tests in the class; method must be static
    static void initShared() { /* expensive setup */ }

    @BeforeEach                                     // runs before EACH test — fresh state
    void setUp() {
        service = new OrderServiceImpl(new InMemoryOrderMapper());
    }

    @AfterEach                                      // runs after each test — cleanup
    void tearDown() { /* reset */ }

    @AfterAll                                       // runs once after all tests
    static void cleanup() { /* shared teardown */ }

    @Test
    void placesOrder() { /* ... */ }

    @Disabled("until payment gateway is ready")     // skip with reason
    @Test
    void chargesPayment() { /* ... */ }
}
```

Prefer `@BeforeEach` over a constructor for setup — clearer intent and works with parameter resolution.

### Naming and display

```java
@DisplayName("Order service")
class OrderServiceTest {

    @Test
    @DisplayName("places an order with CREATED status")
    void placesOrderWithCreatedStatus() { /* ... */ }
}
```

Test names should describe behavior in the method name; `@DisplayName` makes the report human-readable.

### Parameterized tests — kill the loop

```java
@ParameterizedTest
@CsvSource({
    "100, 0,    100",          // amount, discount, expected
    "100, 10,   90",
    "0,   0,    0"
})
void computesTotalCorrectly(BigDecimal amount, BigDecimal discount, BigDecimal expected) {
    var total = service.computeTotal(amount, discount);
    assertThat(total).isEqualByComparingTo(expected);
}
```

Each row is a separate test — failure of one row doesn't stop the others, and the report shows which input failed. Sources: `@ValueSource`, `@CsvSource`, `@MethodSource`, `@EnumSource`, `@NullSource`/`@EmptySource`.

For complex objects, use `@MethodSource`:

```java
static Stream<Arguments> orderScenarios() {
    return Stream.of(
        arguments(new OrderRequest("u1", items(), null, TEN), Status.CREATED),
        arguments(/* ... */)
    );
}

@ParameterizedTest
@MethodSource("orderScenarios")
void handlesEachScenario(OrderRequest req, Status expected) { /* ... */ }
```

### Assertions — prefer AssertJ

```java
import static org.assertj.core.api.Assertions.assertThat;

// ✅ AssertJ: fluent, readable, descriptive failure messages
assertThat(orders)
    .hasSize(3)
    .extracting(Order::getStatus)
    .containsExactly(CREATED, PAID, SHIPPED);

// ❌ JUnit built-in: less readable, weaker messages
assertEquals(3, orders.size());
```

See `testing/test-coverage-assertj.md` for AssertJ patterns in depth.

### Expected exceptions

```java
// ✅ assertThrows — verify type AND inspect
@Test
void rejectsNullUserId() {
    var ex = assertThrows(ValidationException.class,
            () -> service.placeOrder(new OrderRequest(null, List.of(), null, TEN)));
    assertThat(ex.getMessage()).contains("userId");
}

// ❌ @Test(expected = ...) — gone in JUnit 5
// ❌ try-fail-catch pattern — boilerplate, easy to forget fail()
```

### Extensions over inheritance

JUnit 5 allows multiple `@ExtendWith` — composable. Don't use abstract test base classes for setup; use an extension:

```java
public class TestClockExtension implements BeforeEachCallback {
    private Clock clock;
    @Override public void beforeEach(ExtensionContext ctx) {
        clock = Clock.fixed(Instant.parse("2026-07-03T00:00:00Z"), ZoneOffset.UTC);
        Store store = ctx.getStore(NAMESPACE);
        store.put(CLOCK_KEY, clock);
    }
    public static Clock clock(ExtensionContext ctx) {
        return ctx.getStore(NAMESPACE).get(CLOCK_KEY, Clock.class);
    }
}

@ExtendWith(TestClockExtension.class)
class OrderServiceTest {
    @RegisterExtension static TestClockExtension clockExt = new TestClockExtension();
    // ...
}
```

Mockito's `MockitoExtension`, Spring's `SpringExtension` — you compose these.

### Constructor injection in tests

JUnit 5 allows test class constructors; dependencies resolve via `ParameterResolver` extensions. Spring's `@SpringBootTest` supports constructor injection of beans (no `@Autowired` field needed):

```java
@SpringBootTest
class OrderIntegrationTest {
    private final OrderService orderService;

    OrderIntegrationTest(OrderService orderService) {     // constructor injection in tests
        this.orderService = orderService;
    }
}
```

### Nested tests — group related cases

```java
class OrderServiceTest {

    @Nested
    @DisplayName("when placing an order")
    class WhenPlacing {
        @Test void createsWithStatusCreated() { }
        @Test void rejectsEmptyItems() { }
    }

    @Nested
    @DisplayName("when canceling an order")
    class WhenCanceling {
        @Test void setsStatusCanceled() { }
        @Test void refundsPayment() { }
    }
}
```

### Don't

- **Don't** use `Thread.sleep` to wait for async — use `Awaitility` (`await().atMost(2, SECONDS).until(...)`).
- **Don't** depend on test order — tests must be independent. `@Order` exists but is a smell.
- **Don't** leave `System.out.println` in tests — assertions only. If you must debug, log to stderr.
- **Don't** test private methods directly — test through the public API. If a private method is complex enough to need its own test, extract a class.

### Review checklist

- [ ] Test uses `@ParameterizedTest` where it loops over inputs?
- [ ] Assertions via AssertJ (readable, fluent)?
- [ ] Exception type AND message verified (not just type)?
- [ ] Test class lifecycle: `@BeforeEach` over constructor-setup where it matters?
- [ ] Tests independent (no shared mutable state, no order dependency)?
- [ ] No `Thread.sleep` for async — `Awaitility` instead?
- [ ] No `@Disabled` without a reason?

### Context

- **JUnit 4 → 5**: import paths differ (`org.junit.jupiter.api.*` vs `org.junit.*`). Mixing them in one test class breaks. Use 5 only.
- **Spring Boot Test**: `@SpringBootTest` includes `@ExtendWith(SpringExtension.class)` — don't add it again.
- **Cross-ref**: mocking with Mockito in `testing/test-mockito.md`; AssertJ depth in `testing/test-coverage-assertj.md`; Spring slices in `testing/test-spring-boot-test.md`.
