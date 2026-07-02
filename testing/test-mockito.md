---
title: Mockito Patterns
impact: HIGH
impactDescription: Wrong stubbing (over-mock, leaky verify) produces tests that pass but verify nothing
tags: mockito, mocking, stubbing, verify, spy, mockstatic
description: Stub what you need with lenient defaults; verify only behavior that matters; prefer stubbing over spying; mock static sparingly
alwaysApply: true
---

## Mockito Patterns

Mockito is the standard mocking library. The pitfalls are over-mocking (testing mocks instead of code) and over-verifying (brittle tests that break on every refactor).

### Why it matters

- **Over-stubbing** = tests that pass but assert nothing meaningful.
- **Strict verification** = brittle tests; any internal refactor breaks the test even though behavior is unchanged.
- **Mocking the wrong thing** = tests that don't catch real bugs (e.g. mocking the DB out of a DB test).

### The decision: mock vs stub vs spy vs fake

- **Mock**: a test double whose interactions you verify (`verify(mock).save(any())`).
- **Stub**: a double that returns canned answers; you don't verify its calls.
- **Spy**: a real object whose behavior you keep, but you can stub specific methods.
- **Fake**: a working but simplified implementation (e.g. in-memory repository).

**Default to stubs.** Only `verify` when the call is the *point* of the test (e.g. "did we send the email?"). Verifying every internal call produces brittle tests.

### Correct — stub what you need

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock OrderMapper orderMapper;
    @Mock PaymentClient paymentClient;
    @InjectMocks OrderServiceImpl service;

    @Test
    void retrievesExistingOrder() {
        // arrange — stub only what this test exercises
        Order sample = new Order(); sample.setId(1L); sample.setStatus(Status.PAID);
        when(orderMapper.selectById(1L)).thenReturn(sample);

        // act
        OrderResponse resp = service.getOrder(1L);

        // assert — on the result, not on internal calls
        assertThat(resp.status()).isEqualTo(Status.PAID);
    }
}
```

### MockitoExtension strictness

`MockitoExtension` defaults to **strict stubbing** — unused stubs throw `UnnecessaryStubbingException`. This catches dead stubs. If you have a stub you don't always use, either remove it or use `lenient()`:

```java
lenient().when(orderMapper.selectById(anyLong())).thenReturn(sample);
```

But prefer removing it — a stub that's sometimes unused is usually a sign the test is doing too much.

### Argument matchers

```java
when(orderMapper.selectById(eq(1L))).thenReturn(sample);     // eq for exact
when(orderMapper.selectById(anyLong())).thenReturn(sample);  // any
when(paymentClient.charge(argThat(p -> p.amount().signum() > 0))).thenReturn(...);  // custom

verify(orderMapper).insert(argThat(o -> o.getStatus() == Status.CREATED));
```

**Critical**: if you use a matcher for one argument, you must use matchers for **all** arguments of that method. Mixing raw values and matchers throws `InvalidUseOfMatchersException`:

```java
// ❌ mixing
when(mapper.query("literal", anyInt())).thenReturn(...);

// ✅ all matchers
when(mapper.query(eq("literal"), anyInt())).thenReturn(...);
```

### Verify — sparingly

```java
// ✅ verify the side effect that matters
verify(emailSender).send(eq(userId), contains("order confirmation"));
verifyNoMoreInteractions(emailSender);             // nothing else was sent

// ❌ over-verification — breaks when an internal call is added even though behavior is fine
verify(orderMapper, times(1)).insert(any());
verify(orderMapper, times(1)).selectById(anyLong());
verify(paymentClient, times(1)).charge(any());
```

Verify interactions that are observable obligations of the class — "did it tell the email sender?", "did it publish the event?" — not internal orchestration.

### thenThrow for error paths

```java
@Test
void retriesOnTransientFailure() {
    when(paymentClient.charge(any()))
        .thenThrow(new TransientException("timeout"))    // first call throws
        .thenReturn(new PaymentResponse("ok"));          // second succeeds

    service.placeOrder(req);

    verify(paymentClient, times(2)).charge(any());
}
```

### Spy — use rarely

```java
// a spy wraps a real object; you stub specific methods, the rest run for real
OrderService realService = new OrderServiceImpl(realMapper, realClient);
OrderService spy = spy(realService);
doReturn(true).when(spy).isHighPriority(any());           // stub one method

spy.process(order);                                        // real code runs except the stub
```

Spying is a smell — it usually means the class under test has too many responsibilities. Prefer extracting the hard-to-test behavior into a separate dependency you can mock.

### Mocking static methods (Mockito 3.4+)

```java
try (MockedStatic<LocalDateTime> mocked = mockStatic(LocalDateTime.class)) {
    mocked.when(LocalDateTime::now).thenReturn(FIXED_TIME);

    service.placeOrder(req);

    assertThat(...).extracting(Order::getCreateTime).isEqualTo(FIXED_TIME);
}
// static is back to real outside the try-with-resources
```

Use sparingly — only for static methods you can't wrap (legacy code, `LocalDateTime.now` for time, `UUID.randomUUID`). Mocking static is a sign you should extract an injectable dependency (e.g. `Clock`).

### Mocking final classes / constructors

Mockito (with mockito-inline) can mock final classes and constructors. Enable by adding `mockito-inline` artifact (or Mockito 5+, which is inline by default). Use only when you must — preferring non-final types and constructor injection is cleaner.

### Don't

- **Don't mock value objects** (records, DTOs) — construct real instances.
- **Don't mock collections** — use real `List`/`Map` instances.
- **Don't mock the class under test** — you'd be testing the mock.
- **Don't return null from a stub** unless you're testing null handling — silent NPEs.
- **Don't** use `verifyNoMoreInteractions` after every test — it couples the test to internal calls.

### Review checklist

- [ ] Test mocks the class under test? (Should mock its dependencies instead.)
- [ ] Excessive `verify(...)` calls — every internal interaction verified?
- [ ] Unused stubs (strict stubbing will catch, but check)?
- [ ] Mixed raw value + matcher in a single stubbing?
- [ ] `MockedStatic` used where injecting `Clock` would work?
- [ ] Spy used where refactoring would remove the need?
- [ ] Returning null from a stub without explicit reason?

### Context

- **Mockito version**: Mockito 5+ is inline-by-default (mocks final); 4.x needs `mockito-inline`. Spring Boot's BOM aligns these — use the managed version.
- **`@MockBean`** (Spring): replaces a bean in the context with a mock. Convenient but expensive — each `@MockBean` triggers a context cache miss. Prefer plain `@Mock` + `@InjectMocks` for unit tests; reserve `@MockBean` for slice tests where you need the Spring context.
- **Cross-ref**: `@MockBean` in slice tests in `test-spring-boot-test.md`; AssertJ assertion depth in `test-coverage-assertj.md`.
