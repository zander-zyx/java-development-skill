---
title: Spring Boot Test Slices
impact: HIGH
impactDescription: Slices give fast focused tests; @SpringBootTest is overkill for most controller/mapper verification
tags: springboottest, webmvctest, datajpatest, mockbean, slice
description: Use @WebMvcTest for controllers, @DataJpaTest/@MybatisPlusTest for persistence, @SpringBootTest for full wiring
---

## Spring Boot Test Slices

Spring Boot's slice annotations start only the relevant context. Use them by default; reach for full `@SpringBootTest` only when you need the whole stack.

### Why it matters

- **Speed**: a slice loads in ~1 second; `@SpringBootTest` can take 10+ seconds. Over a suite of hundreds of tests, that's minutes vs hours.
- **Focus**: a slice test fails for a slice-specific reason (controller mapping wrong, query wrong), not because some unrelated bean failed to wire.
- **Cache granularity**: Spring caches the test context by configuration. Slice tests share cache; `@SpringBootTest` with `@MockBean` pollutes cache and forces rebuilds.

### @WebMvcTest — controllers

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvc mockMvc;
    @MockBean OrderService orderService;                // service is mocked; only MVC layer is real

    @Test
    void returns404WhenOrderMissing() throws Exception {
        when(orderService.getOrder(99L)).thenThrow(new OrderNotFoundException(99L));

        mockMvc.perform(get("/api/orders/99"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.title").value("Order Not Found"));
    }

    @Test
    void rejectsBlankUserId() throws Exception {
        var body = "{\"items\":[],\"amount\":10}";
        mockMvc.perform(post("/api/orders").contentType(APPLICATION_JSON).content(body))
            .andExpect(status().isBadRequest());        // @Valid fires
    }
}
```

This verifies: routing, JSON (de)serialization, validation, exception handling via `@RestControllerAdvice`. It does NOT verify: the service logic, the DB. Pair it with a unit test of the service.

### @DataJpaTest — JPA repositories

```java
@DataJpaTest                                           // default: H2 in-memory, rolls back per test
@Testcontainers                                        // (combine with Testcontainers to use real DB)
class OrderRepositoryTest {
    @Autowired OrderRepository repo;
    @Autowired TestEntityManager em;

    @Test
    void findByStatusReturnsOnlyMatching() {
        em.persist(new Order(Status.PAID));
        em.persist(new Order(Status.CREATED));

        List<Order> paid = repo.findByStatus(Status.PAID);

        assertThat(paid).hasSize(1);
    }
}
```

`@DataJpaTest` defaults to H2 and `@Transactional` rollback. To use real MySQL/PG, combine with Testcontainers and `@AutoConfigureTestDatabase(replace = NONE)`:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class OrderRepositoryTest {
    @Container @ServiceConnection static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");
    // ...
}
```

### MyBatis-Plus mapper tests

There's no first-party `@MybatisPlusTest` slice in MP, but the mybatis-plus-boot-starter-test artifact provides one, or you can use `@MybatisTest` (MyBatis own slice). Common pattern:

```java
@SpringBootTest                                          // simplest: full context but with H2/containers
@ActiveProfiles("test")
class OrderMapperTest {
    @Autowired OrderMapper orderMapper;

    @Test
    void insertsAndSelects() {
        Order o = new Order(); o.setUserId("u1"); o.setStatus("CREATED");
        orderMapper.insert(o);
        Order found = orderMapper.selectById(o.getId());
        assertThat(found.getUserId()).isEqualTo("u1");
    }
}
```

For a true slice (faster), use `@MybatisPlusTest` from `mybatis-plus-boot-starter-test` (MP 3.5.4+), which loads only mapper + datasource.

### @SpringBootTest — full integration

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OrderE2ETest {
    @LocalServerPort int port;
    @Autowired TestRestTemplate http;

    @Test
    void placeOrderRoundTrip() {
        ResponseEntity<Void> r = http.postForEntity("/api/orders", request, Void.class);
        assertThat(r.getStatusCode()).isEqualTo(CREATED);
    }
}
```

Use `@SpringBootTest` when:
- You need the full filter chain (security, exception advice) in the test path.
- You're verifying wiring across slices (service + mapper + DB).
- A bug only reproduces with the real context.

### @MockBean — and its cost

```java
@MockBean OrderService orderService;                    // replaces the bean in the context
```

Convenient, but each unique combination of `@MockBean` creates a **new Spring context** (cache key changes). If two test classes both `@MockBean OrderService`, they share; if one also `@MockBean PaymentClient`, that's three contexts. Contexts are expensive (seconds each).

**For unit tests**, prefer plain `@Mock` + `@InjectMocks` (no Spring). Reserve `@MockBean` for slice tests.

### @Import for custom config in slices

A slice doesn't load every bean. If your controller needs a specific config (ObjectMapper bean, converter), import it:

```java
@WebMvcTest(OrderController.class)
@Import({JacksonConfig.class, OrderDtoConverter.class})
class OrderControllerTest { }
```

### Test profile

Use `application-test.yml` + `@ActiveProfiles("test")` for test-only config:

```yaml
# application-test.yml
spring:
  jpa:
    hibernate:
      ddl-auto: create-drop
logging:
  level:
    org.hibernate.SQL: debug
```

### Review checklist

- [ ] `@SpringBootTest` used where `@WebMvcTest`/`@DataJpaTest` would suffice?
- [ ] Excessive `@MockBean` declarations forcing many context rebuilds?
- [ ] Slice test missing `@Import` for a required config bean?
- [ ] H2 used for what should be a real-DB test (different dialect)?
- [ ] `@Transactional` rollback used appropriately for DB tests?
- [ ] `@ActiveProfiles("test")` for test-only config?

### Context

- **Context caching**: Spring caches test application contexts by their configuration signature. Keep the signature stable across tests to maximize cache hits.
- **`@DirtiesContext`**: forces context teardown after the test class. Use sparingly — it's expensive. Prefer cleanup via `@Transactional` rollback.
- **Cross-ref**: layering rationale in `testing/test-layering.md`; Testcontainers in `testing/test-testcontainers.md`; Mockito in `testing/test-mockito.md`.
