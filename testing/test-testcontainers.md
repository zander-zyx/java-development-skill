---
title: Testcontainers for Real Boundaries
impact: HIGH
impactDescription: Testcontainers gives you a real DB/Redis/Kafka in tests, catching SQL and protocol bugs that in-memory doubles miss
tags: testcontainers, integration, docker, serviceconnection, mysql, redis
description: Use @ServiceConnection (Spring Boot 3.1+) to auto-wire containers; reuse containers to keep tests fast
alwaysApply: true
---

## Testcontainers for Real Boundaries

In-memory databases (H2) and mocks hide bugs — different SQL dialects, missing indexes, transactions that behave differently. Testcontainers spins up the real MySQL/PostgreSQL/Redis in a Docker container for the test, then tears it down.

### Why it matters

- **Real dialect catches bugs** — H2 accepts SQL that MySQL rejects (e.g. reserved words, JSON operators, window functions). A test that passes on H2 fails in prod.
- **Real behavior** — Redis pipelining, Kafka ordering, PostgreSQL advisory locks all behave as prod.
- **Reproducibility** — the container image is pinned; tests run identically on every developer's machine and CI.

### Setup (Spring Boot 3.1+ — use @ServiceConnection)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mysql</artifactId>
    <scope>test</scope>
</dependency>
```

```java
@SpringBootTest
@Testcontainers
class OrderIntegrationTest {

    @Container
    @ServiceConnection                                    // ✅ auto-wires datasource.url/user/pass
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");

    @Autowired OrderService orderService;

    @Test
    void persistsAndRetrieves() {
        orderService.placeOrder(req);
        // ...assertions against real MySQL
    }
}
```

`@ServiceConnection` (Spring Boot 3.1+) eliminates the boilerplate of `@DynamicPropertySource` — Spring inspects the container and configures the datasource automatically.

### Pre-3.1 — manual property wiring

If you're on SB 2.x or pre-3.1, use `@DynamicPropertySource`:

```java
@Container
static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");

@DynamicPropertySource
static void registerProps(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", mysql::getJdbcUrl);
    registry.add("spring.datasource.username", mysql::getUsername);
    registry.add("spring.datasource.password", mysql::getPassword);
}
```

### Reuse containers — keep tests fast

Starting a container per test class is slow (MySQL cold start ~10s). Enable **reuse** so a container survives across test runs:

```java
static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8")
    .withReuse(true);
```

And in `~/.testcontainers.properties` (user-wide):

```properties
testcontainers.reuse.enable=true
```

The same container persists between test runs (even between IDE runs), cutting setup to milliseconds. Spring's context cache keeps the wired beans; with reuse on, even a fresh JVM reuses the container.

### Container as a @Bean (Spring pattern)

For a single shared container across the whole test suite, expose it as a bean:

```java
@TestConfiguration
public class ContainerConfig {
    @Bean
    @ServiceConnection
    @RestartScope                                        // keeps container between context restarts
    MySQLContainer<?> mysql() {
        return new MySQLContainer<>("mysql:8").withReuse(true);
    }
}

@SpringBootTest
@Import(ContainerConfig.class)
class OrderIntegrationTest { }
```

### Schema initialization

For MyBatis-Plus/JPA, you need the schema. Options:

```java
MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8")
    .withInitScript("schema.sql");                      // runs a classpath script

// or map a SQL file as a volume
new PostgreSQLContainer<>("postgres:16")
    .withCopyFileToContainer(MountableFile.forClasspathResource("schema.sql"),
                             "/docker-entrypoint-initdb.d/schema.sql");

// or let Hibernate create the schema (JPA only)
// spring.jpa.hibernate.ddl-auto=create-drop in test profile
```

For MyBatis-Plus, prefer the init script approach — there's no auto-DDL.

### Other common containers

```java
@Container static GenericContainer<?> redis = new GenericContainer<>("redis:7").withExposedPorts(6379);

@Container static KafkaContainer kafka = new KafkaContainer();

@Container static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16");

ToxiproxyContainer toxiproxy = new ToxiproxyContainer();  // for network fault simulation
```

Each has a `@ServiceConnection`-aware variant in Spring Boot 3.1+ where applicable.

### Don't

- **Don't** use H2 "in MySQL mode" to test MyBatis-Plus — mode is partial; you'll get false confidence.
- **Don't** start a container inside a `@Test` method — use `@Container` static fields so one container serves the whole class.
- **Don't** forget `withReuse(true)` for frequently-run tests; otherwise CI/IDE runs pay the cold start every time.
- **Don't** assert on data that another test mutated — each test should seed its own data (Testcontainers rollback-per-test, or `@Sql`/`@Transactional` rollback).

### Data isolation

For integration tests, the cleanest isolation is **transactional rollback**:

```java
@SpringBootTest
@Transactional                                       // each test rolls back at the end
class OrderIntegrationTest { ... }
```

The test runs in a transaction that Spring rolls back, so the DB is clean for the next test. Note: this hides transaction-boundary bugs (commit semantics differ), so for testing actual `@Transactional` behavior, don't roll back — instead use `@DirtiesContext` or a fresh container.

### Review checklist

- [ ] Tests against H2 that should test against real MySQL/PG?
- [ ] `@ServiceConnection` used (SB 3.1+) instead of manual `@DynamicPropertySource`?
- [ ] `withReuse(true)` for the main DB container?
- [ ] Container declared as static field, not instance or local?
- [ ] Schema init via init script, not relying on leftover state?
- [ ] Test data isolated (transactional rollback or per-test seeding)?

### Context

- **Docker required**: Testcontainers needs Docker on the machine running tests. CI must have Docker-in-Docker or a sidecar.
- **Spring Boot 3.1 `@ServiceConnection`**: replaces `@DynamicPropertySource` for many container types (MySQL, PostgreSQL, Redis, Kafka, MongoDB, etc.).
- **CI speed**: with reuse + parallel test execution, container-based tests can run nearly as fast as in-memory ones. Without reuse, they're slow.
- **Cross-ref**: integration test layering in `testing/test-layering.md`; MyBatis-Plus + schema in `spring-boot/sb-mybatis-plus.md`; datasource config in `spring-boot/sb-config-profiles.md`.
