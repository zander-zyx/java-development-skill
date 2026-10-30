---
title: Test Layering Strategy
impact: HIGH
impactDescription: Right layer = fast feedback + real coverage; wrong layer = slow suite that misses bugs
tags: testing, layering, unit, integration, slice, pyramid
description: Use unit tests for logic, Spring slices for wiring, integration tests for boundaries; aim for the pyramid not the cone
---

## Test Layering Strategy

Match the test type to what you're verifying. Wrong layer = either too slow (integration for pure logic) or too shallow (unit test for a DB query that mocks the DB away).

### Why it matters

The ice-cream-cone test suite (many E2E, few unit tests) is a real project killer: a 40-minute CI run means developers batch changes and stop trusting tests; flaky full-stack tests get `@Disabled` one by one until coverage is theater; and a mocked-away DB query "passes" while the real SQL is wrong — the bug ships and the suite stays green. Layer choice is the difference between a suite that catches regressions in seconds and one that catches them in production.

### Correct — pick the layer by the question

```java
// Bad (Avoid) — integration test to verify arithmetic
@SpringBootTest
class DiscountTest {
    @Test void tenPercentOff() { assertThat(service.price(req)).isEqualTo(90); }   // 20s context boot for one line of logic
}

// Good (Preferred) — unit test for logic, slice for wiring, integration for boundaries
@ExtendWith(MockitoExtension.class)          // milliseconds
class DiscountTest {
    @Test void tenPercentOff() { assertThat(new Pricer(clock).price(req)).isEqualTo(90); }
}
```

### The layers

```
        ┌─────────────────────┐
        │  End-to-End (few)   │  @SpringBootTest + real HTTP, full stack. Slowest.
        ├─────────────────────┤
        │ Integration (some)  │  @SpringBootTest with Testcontainers DB. Real boundaries.
        ├─────────────────────┤
        │   Slice (some)      │  @WebMvcTest, @DataJpaTest, @MybatisPlusTest. Partial context.
        ├─────────────────────┤
        │   Unit (many)       │  Plain JUnit, mocked deps. Milliseconds.
        └─────────────────────┘
```

Aim for the **pyramid**: many unit tests, fewer slice/integration, very few end-to-end. The "ice-cream cone" (many E2E, few unit) is slow, flaky, and hides where bugs are.

### Which test for which question

| Question | Test type | Example |
|----------|-----------|---------|
| "Does this logic compute the right discount?" | Unit | `pricingServiceTest`, pure JUnit + mocked deps |
| "Does the controller map HTTP → service correctly?" | Slice | `@WebMvcTest(OrderController.class)` + version-appropriate `@MockitoBean`/`@MockBean` |
| "Does the JPA/MyBatis query return what I expect against a real schema?" | Slice/Integration | `@DataJpaTest` or `@SpringBootTest` + Testcontainers |
| "Do the service + DB + mapper actually wire together and persist?" | Integration | `@SpringBootTest` + Testcontainers MySQL |
| "Does the full HTTP path work, including security + JSON?" | E2E | `@SpringBootTest(webEnvironment=RANDOM_PORT)` + `TestRestTemplate` |

### Unit tests — fast, isolated, many

A unit test verifies one class with its dependencies mocked/stubbed. Milliseconds. No Spring context.

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock OrderMapper orderMapper;
    @Mock PaymentClient paymentClient;
    @InjectMocks OrderServiceImpl service;

    @Test
    void placesOrderSavesAndCharges() {
        when(orderMapper.insert(any())).thenAnswer(inv -> { ((Order) inv.getArgument(0)).setId(1L); return 1; });

        service.placeOrder(new OrderRequest("u1", List.of(), null, TEN));

        verify(orderMapper).insert(any(Order.class));
        verify(paymentClient).charge(any());
    }
}
```

See `testing/test-junit5.md` for the JUnit 5 patterns, `testing/test-mockito.md` for stubbing.

### Slice tests — partial Spring context

Spring Boot's slice annotations start only the relevant slice of context — fast and focused:

- **`@WebMvcTest(OrderController.class)`** — loads the controller + MVC infra (JSON, validation), mocks services. Verifies HTTP mapping, DTO binding, validation. Doesn't touch DB.
- **`@DataJpaTest`** — loads JPA repos + an in-memory or Testcontainers DB. Verifies queries.
- **`@MybatisPlusTest`** (MP) — loads MP mappers + DB. Verifies queries.
- **`@JsonTest`** — loads Jackson. Verifies serialization.

These run in ~1-2 seconds vs ~10+ for a full `@SpringBootTest`.

### Integration tests — real boundaries

```java
@SpringBootTest
@Testcontainers
class OrderIntegrationTest {
    @Container static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", mysql::getJdbcUrl);
        // ...
    }

    @Test void orderPersistsAndIsRetrievable() {
        // exercise the real service → mapper → real MySQL
    }
}
```

Use Testcontainers so the DB is the real engine (not H2's "almost MySQL"). See `testing/test-testcontainers.md`.

### End-to-end — sparingly

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrderE2ETest {
    @LocalServerPort int port;
    @Autowired TestRestTemplate http;

    @Test void placeOrderReturns201() {
        ResponseEntity<Void> r = http.postForEntity("/api/orders", request, Void.class);
        assertThat(r.getStatusCode()).isEqualTo(CREATED);
    }
}
```

A handful per service — these verify the full path including security filter, JSON serialization, error advice. They're slow and flaky-prone; don't make them your main suite.

### How many of each — a guideline

- **Unit**: every public service method, every branch of non-trivial logic. Hundreds.
- **Slice**: each controller endpoint (happy path + validation failure), each non-trivial query. Tens.
- **Integration**: each feature's "create + read + update + delete" flow against real DB. Tens.
- **E2E**: critical paths (signup, checkout, payment). A few.

### Don't mock the thing under test

```java
// ❌ testing the mock
@Mock OrderService orderService;
@Test void test() {
    when(orderService.find(1L)).thenReturn(...);
    assertThat(orderService.find(1L)).isEqualTo(...);   // trivially true, verifies nothing
}
```

Mock the **dependencies** of the class under test, never the class itself.

### Don't mock types you don't own

Mocking `RestClient`, `Clock`, or third-party classes creates tests coupled to a library you don't control. Wrap them in your own interface (`PaymentGateway`) and mock that. When the library changes, only your adapter breaks, not every test.

### When NOT to use

- Do not force a layering pyramid onto a small library with no Spring context — plain unit tests are the whole pyramid there.
- Do not add Testcontainers integration tests during a hotfix; verify the fix at the narrowest layer and add the regression test as a follow-up.
- Teams with an established, working test strategy should keep it; this rule guides new work, not rewrites of existing suites.

### Context

- **Coverage**: 100% coverage is not the goal — covering meaningful behavior is. See `testing/test-coverage-assertj.md`.
- **Test speed budget**: aim for the full unit suite under 10 seconds. Slower than that and developers stop running tests locally.
- **Cross-ref**: slice test specifics in `testing/test-spring-boot-test.md`; Testcontainers in `testing/test-testcontainers.md`; mocking in `testing/test-mockito.md`.
