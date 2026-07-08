---
title: REST Client Selection
impact: MEDIUM
impactDescription: Choosing the right client prevents deprecated API lock-in, blocking-pool exhaustion, and refactoring debt
tags: restclient, resttemplate, webclient, http-client, deprecated
description: Use RestClient for synchronous calls (Spring 6.1+); WebClient for reactive/streams; do not start new code with RestTemplate
---

## REST Client Selection

Spring offers three HTTP clients. Pick by use case; do **not** start new code with `RestTemplate` — as of Spring Framework 7.0, it is deprecated in favor of `RestClient`.

| Client | Introduced | Style | Use when |
|--------|-----------|-------|----------|
| `RestClient` | Spring 6.1 / SB 3.2 | synchronous, fluent | Default for sync calls |
| `WebClient` | Spring 5.0 | reactive (Netty) | Reactive `Mono`/`Flux`, streaming, many concurrent idle conns |
| `RestTemplate` | Spring 3.0 (2009) | synchronous, template | Legacy only — don't start new code |

### Why it matters

- `RestTemplate` is deprecated in Spring Framework 7.0 in favor of `RestClient` — new code using it accumulates migration debt.
- `WebClient` used in a servlet app drags in Netty and the reactive stack just to make a call — overkill and a different mental model.
- `RestClient` gives the fluent API of WebClient over a synchronous JDK HttpClient — the modern sweet spot.

### Correct — RestClient (default for synchronous)

Configure as a bean with timeouts:

```java
@Configuration
public class HttpClientConfig {

    @Bean
    RestClient paymentRestClient(PaymentProperties props) {
        ClientHttpRequestFactorySettings settings = ClientHttpRequestFactorySettings.DEFAULTS
            .withConnectTimeout(Duration.ofSeconds(3))
            .withReadTimeout(Duration.ofSeconds(10));
        return RestClient.builder()
                .baseUrl(props.baseUrl())
                .requestFactory(ClientHttpRequestFactoryBuilder.detect().build(settings))
                .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + props.token())
                .build();
    }
}
```

Use it:

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class PaymentClient {
    private final RestClient paymentRestClient;

    public PaymentResponse charge(PaymentRequest req) {
        return paymentRestClient.post()
                .uri("/charge")
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .onStatus(status -> status.is4xxClientError(), (req2, resp) -> {
                    throw new PaymentDeclinedException(new String(resp.getBody().readAllBytes()));
                })
                .body(PaymentResponse.class);
    }
}
```

`onStatus` lets you map HTTP statuses to domain exceptions cleanly — prefer it over parsing error bodies after the fact.

### Correct — WebClient (when reactive/streaming)

```java
@Service
@RequiredArgsConstructor
public class PriceStreamClient {
    private final WebClient webClient;

    public Flux<PriceTick> stream(String symbol) {
        return webClient.get()
                .uri("/prices/{symbol}/stream", symbol)
                .retrieve()
                .bodyToFlux(PriceTick.class);
    }
}
```

Use WebClient when the consumer is itself reactive (`Mono`/`Flux`), you stream unbounded data, or you hold thousands of idle connections (Netty's non-blocking model wins there). For one-shot synchronous calls in a servlet app, RestClient is simpler.

### Incorrect

New code with RestTemplate:

```java
// ❌ deprecated in Spring 7; new code shouldn't use this
@Bean
RestTemplate restTemplate() { return new RestTemplate(); }
```

WebClient in a pure servlet app just for sync calls:

```java
// ❌ pulls in reactive Netty stack you don't use; .block() defeats the purpose
@Service
public class PaymentClient {
    private final WebClient webClient;
    public PaymentResponse charge(PaymentRequest req) {
        return webClient.post().uri("/charge").bodyValue(req)
                .retrieve().bodyToMono(PaymentResponse.class)
                .block(Duration.ofSeconds(10));   // blocking on reactive — anti-pattern
    }
}
```

### Resilience layer

For calls to external services, wrap the client with retries + circuit breaking. **Resilience4j** is the standard (Hystrix is EOL):

```java
@Configuration
public class ResilienceConfig {
    @Bean
    CircuitBreaker paymentCb(CircuitBreakerRegistry registry) {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
                .failureRateThreshold(50)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .slidingWindowSize(20)
                .build();
        return registry.circuitBreaker("payment", config);
    }
}

// decorate the call
return CircuitBreakerDecorator.decorateSupplier(circuitBreaker,
        () -> restClient.post().uri("/charge").body(req).retrieve().body(PaymentResponse.class))
    .get();
```

Or use Spring's `@CircuitBreaker` from spring-cloud-circuitbreaker for declarative form.

### HttpClient 5 (replaces HttpClient 4 in SB 3.1+)

If you need Apache HttpClient as the underlying transport, use **HttpClient 5**, not 4. SB 3.1 dropped dependency management for HttpClient 4:

```xml
<dependency>
    <groupId>org.apache.httpcomponents.client5</groupId>
    <artifactId>httpclient5</artifactId>
</dependency>
```

### Context

- **Timeouts**: always set connect + read timeouts. Default `RestClient` has none → hangs forever on a stuck server.
- **Connection pooling**: the JDK HttpClient pools connections; tune via system properties if needed (`jdk.httpclient.connectionPoolSize`).
- **Reactive decision**: pick WebClient when *most* of your handlers are reactive, not for one endpoint — mixing stacks in one app is confusing.
- **Cross-ref**: observability of HTTP client calls (tracing, metrics) is in `spring-boot/sb-actuator-health.md`; the deprecation timeline is in `spring-boot/sb-migration-2-to-3.md`.
