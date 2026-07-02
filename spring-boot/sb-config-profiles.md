---
title: Configuration and Profiles
impact: MEDIUM
impactDescription: Correct externalized config avoids hardcoded env values and 12-factor violations
tags: config, profiles, application-yml, spring-config-import, secrets
description: Externalize config via application.yml + profiles; use spring.config.import over bootstrap; never commit secrets
---

## Configuration and Profiles

Externalize all environment-specific values into `application.yml`, split per-environment via profiles, and pull secrets from env vars or a config server. Never hardcode URLs, credentials, or feature flags.

### Why it matters

- Hardcoded values force a rebuild to change environment.
- Profile-less config makes "test ran against prod DB" accidents possible.
- Committed secrets (`spring.datasource.password=...`) leak via git history and are impossible to fully scrub.

### Correct — layered config with profiles

`application.yml` (shared defaults):

```yaml
spring:
  application:
    name: shop-service
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/shop}
    username: ${DB_USERNAME:shop}
    password: ${DB_PASSWORD}            # no default → fails fast if missing
  jpa:
    open-in-view: false                 # see sb-jpa-repository.md
server:
  port: ${PORT:8080}
management:
  endpoints.web.exposure.include: health,info,metrics
app:
  order:
    max-items-per-cart: 50
```

`application-dev.yml` (dev profile overrides):

```yaml
spring:
  jpa:
    show-sql: true
    hibernate.ddl-auto: update
logging:
  level:
    com.acme: DEBUG
    org.hibernate.SQL: DEBUG
```

`application-prod.yml`:

```yaml
spring:
  jpa:
    hibernate.ddl-auto: validate        # never auto-DDL in prod
    show-sql: false
logging:
  level:
    root: WARN
    com.acme: INFO
```

Run with `--spring.profiles.active=dev` or env var `SPRING_PROFILES_ACTIVE=prod`.

### Environment variables over inline values

Use `${VAR:default}` syntax. Required values get no default (fail fast):

```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}            # ✅ fails startup if unset
    url: ${DB_URL:jdbc:postgresql://localhost:5432/shop}   # default for local dev
```

### Type-safe config with @ConfigurationProperties

For grouped/nested config, bind to a record via `@ConfigurationProperties` — don't sprinkle `@Value` everywhere:

```java
@ConfigurationProperties(prefix = "app.order")
public record OrderProperties(int maxItemsPerCart, Duration reservationTimeout) {}

@Configuration
@EnableConfigurationProperties(OrderProperties.class)
class OrderConfig {}

@Service
@RequiredArgsConstructor
class OrderService {
    private final OrderProperties props;          // injected, typed, validated

    void validate(List<OrderItem> items) {
        if (items.size() > props.maxItemsPerCart()) {
            throw new CartLimitException(props.maxItemsPerCart());
        }
    }
}
```

### spring.config.import (replaces bootstrap.yml)

Since Spring Boot 2.4, import additional config — including a config server — via `spring.config.import` instead of the deprecated `bootstrap.yml`:

```yaml
spring:
  config:
    import:
      - optional:configserver:https://config.acme.com
      - classpath:additional-common.yml
      - file:./override.yml
```

This works identically in 2.x and 3.x; it is the modern mechanism for config server, Vault, and AWS Secrets Manager integration.

### Incorrect

Hardcoded values:

```java
// ❌ rebuild required to change env
@Value("jdbc:postgresql://prod-db:5432/shop")
private String dbUrl;
```

Committed secrets:

```yaml
# ❌ in application-prod.yml committed to git
spring:
  datasource:
    password: SuperSecret123            # never commit; rotate immediately if found
```

Scattered `@Value`:

```java
// ❌ no validation, no grouping, hard to test
@Value("${app.order.max-items}") private int maxItems;
@Value("${app.order.timeout}") private String timeout;  // String? should be Duration
```

### Secrets handling

- **Local dev**: put real-ish secrets in `application-local.yml` and gitignore it; never use a real prod credential locally.
- **Prod**: inject via env var (`DB_PASSWORD`), Kubernetes secret, or Vault/Spring Cloud Config. The app reads `${DB_PASSWORD}` and never sees the literal.
- **Found a committed secret?**: treat it as compromised — rotate immediately, don't just delete the line (git history retains it).

### Context

- **Profile activation order**: `application.yml` is always loaded; profile files override it. Multiple active profiles apply in declaration order; later wins.
- **Test profiles**: use `@ActiveProfiles("test")` on test classes to load `application-test.yml` (e.g. testcontainers DB).
- **YAML gotcha**: YAML treats `on`/`off`/`yes`/`no` as booleans. Quote string config: `mode: "off"`.
- **Cross-ref**: actuator exposure of config is in `sb-actuator-health.md`; test profile usage in `testing/test-spring-boot-test.md`.
