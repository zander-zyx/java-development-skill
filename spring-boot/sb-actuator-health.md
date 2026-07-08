---
title: Actuator, Health, and Observability
impact: MEDIUM
impactDescription: Proper actuator exposure enables liveness/readiness probes and metrics without leaking sensitive endpoints
tags: actuator, health, metrics, observability, micrometer, prometheus
description: Expose only health/info/metrics in prod, configure liveness/readiness groups, scrape Prometheus metrics
---

## Actuator, Health, and Observability

Actuator gives you health checks, metrics, and runtime info. Expose what each environment needs; lock down in prod.

### Why it matters

- **K8s probes need it**: liveness/readiness groups drive pod restarts and traffic routing.
- **Metrics feed your dashboards**: Micrometer + actuator `/metrics` is the standard Prometheus scrape target.
- **Over-exposure**: `/env`, `/heapdump`, `/threaddump` leak secrets and internals — never expose in prod without auth.

### Configure per environment

```yaml
# application.yml (shared)
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  endpoint:
    health:
      show-details: when_authorized     # hide DB URLs from anonymous
      probes:
        enabled: true                    # expose /health/liveness and /health/readiness
      group:
        liveness:
          include: ping                  # minimal — just "is the JVM up"
        readiness:
          include: db, redis             # can serve traffic only if deps reachable
  metrics:
    tags:
      application: ${spring.application.name}
    distribution:
      percentiles-histogram:
        http.server.requests: true
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
```

### Liveness vs Readiness (Kubernetes)

- **Liveness** (`/health/liveness`): "is the app running and not deadlocked?" Map to K8s `livenessProbe`. Failure → restart the pod.
- **Readiness** (`/health/readiness`): "is the app ready to serve requests (DB connected, warmed up)?" Map to `readinessProbe`. Failure → remove from Service endpoints, no traffic, no restart.

Spring updates these from `ApplicationAvailability`. They're `UP` after the `ApplicationReadyEvent`; readiness drops to `OUT_OF_SERVICE` if a health indicator fails.

```yaml
# k8s deployment
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 60
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
```

### Custom health indicators

Add a domain-specific check by implementing `HealthIndicator`:

```java
@Component("license")
@Slf4j
public class LicenseHealthIndicator implements HealthIndicator {
    private final LicenseService licenseService;

    @Override
    public Health health() {
        try {
            LicenseStatus s = licenseService.check();
            return s.valid()
                ? Health.up().withDetail("expires", s.expiresAt()).build()
                : Health.down().withDetail("reason", s.reason()).build();
        } catch (Exception e) {
            log.warn("License health check failed", e);
            return Health.down(e).build();
        }
    }
}
```

Add `"license"` to the readiness group to make it block traffic.

### Metrics with Micrometer

Inject `MeterRegistry` and create timers/counters/gauges:

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final MeterRegistry meterRegistry;

    public Order placeOrder(OrderRequest req) {
        return Timer.builder("order.place")
                .tag("channel", req.channel())
                .register(meterRegistry)
                .record(() -> doPlaceOrder(req));
    }
}
```

For HTTP endpoint metrics, the `http.server.requests` timer is auto-recorded — just enable the histogram for percentiles (done above).

### Prometheus scrape

Add the dependency and the `/actuator/prometheus` endpoint is auto-exposed:

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

Prometheus config:

```yaml
scrape_configs:
  - job_name: shop-service
    metrics_path: /actuator/prometheus
    static_configs:
      - targets: ['shop:8080']
```

### Distributed tracing (Spring Boot 3.x)

Micrometer Tracing (replaces Spring Cloud Sleuth) auto-wires trace propagation. Add a backend exporter (Zipkin, OTLP, Tempo):

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>otlp-exporter</artifactId>
</dependency>
```

```yaml
management:
  tracing:
    sampling.probability: 1.0           # 100% in dev; ~10% in prod
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
```

TraceId/Spans propagate via MDC into logs automatically — use `%X{traceId}` in your log pattern to include it.

### Incorrect

Expose everything:

```yaml
# ❌ exposes /env (secrets), /heapdump (memory), /shutdown (kill switch)
management:
  endpoints.web.exposure.include: "*"
```

Show details to anonymous:

```yaml
# ❌ /actuator/health now returns DB URLs, credentials masked but real
management.endpoint.health.show-details: always
```

No timeout on probes — if a health check hangs, K8s times out and the pod stays in a bad state longer. Keep health checks fast (<1s); offload slow checks to a separate async-updated indicator.

### Context

- **show-details = `never`**: hides health detail entirely. `when_authorized` (default) reveals details only to authorized callers. Use `never` in strictly prod if you don't want to leak indicator names.
- **Probe caching**: K8s calls probes frequently; keep `HealthIndicator` implementations cheap or cache their result with a short TTL.
- **Heapdump access**: never expose `/heapdump` to the network — it's a full memory image, contains all data including secrets. Restrict to localhost or JMX.
- **Cross-ref**: traceId in error responses relates to `spring-boot/sb-exception-handling.md`; HTTP client metrics tie into `spring-boot/sb-rest-client.md`.
