---
title: Global Exception Handling
impact: HIGH
impactDescription: A single @RestControllerAdvice gives consistent error responses and centralizes error logic
tags: exceptions, restcontrolleradvice, error-responses, validation, problem-details
description: Handle all exceptions in one @RestControllerAdvice; return RFC 7807 ProblemDetail; never leak stack traces
---

## Global Exception Handling

Centralize HTTP exception handling in a single `@RestControllerAdvice`. Return structured error bodies. Never let raw stack traces reach the client.

### Why it matters

- **Consistency** — without a central handler, each controller invents its own error shape. Clients can't parse errors uniformly.
- **Information leakage** — a default 500 with a Java stack trace reveals packages, versions, sometimes SQL — useful to attackers.
- **Boilerplate** — without an advice, every controller method wraps in try/catch, repeating the same mapping logic.

### Correct — one RestControllerAdvice

Define your domain exceptions as a small hierarchy, then map each to an HTTP response in one place.

Domain exceptions:

```java
public abstract class ShopException extends RuntimeException {
    public ShopException(String message) { super(message); }
}

public class OrderNotFoundException extends ShopException {
    private final Long orderId;
    public OrderNotFoundException(Long orderId) {
        super("Order " + orderId + " not found");
        this.orderId = orderId;
    }
    public Long getOrderId() { return orderId; }
}

public class CartLimitExceededException extends ShopException {
    public CartLimitExceededException(int limit) {
        super("Cart exceeds limit of " + limit + " items");
    }
}
```

The advice:

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ProblemDetail handleNotFound(OrderNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Order Not Found");
        problem.setProperty("orderId", ex.getOrderId());   // extra structured field
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)   // @Valid failures
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "Request validation failed");
        Map<String, String> fields = ex.getBindingResult().getFieldErrors().stream()
                .collect(toMap(FieldError::getField, FieldError::getDefaultMessage, (a, b) -> a));
        problem.setProperty("errors", fields);
        return problem;
    }

    @ExceptionHandler(Exception.class)                         // catch-all last resort
    public ProblemDetail handleUnexpected(Exception ex) {
        log.error("Unhandled exception", ex);                  // log full trace server-side
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected error");
        problem.setProperty("traceId", MDC.get("traceId"));   // let support correlate
        return problem;                                        // no stack trace to client
    }
}
```

### RFC 7807 ProblemDetail (Spring 6+)

Spring Boot 3.x ships `org.springframework.http.ProblemDetail` implementing RFC 7807. Prefer it over custom error JSON — clients and tools increasingly understand the standard shape:

```json
{
  "type": "about:blank",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order 42 not found",
  "instance": "/orders/42",
  "orderId": 42
}
```

Enable it as the default for Spring MVC errors too:

```yaml
spring:
  mvc:
    problem-details:
      enabled: true
```

### Throwing in controllers/services

Don't catch-and-rethrow in the service just to log — let it propagate to the advice:

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository repo;

    public Order get(Long id) {
        return repo.findById(id)
            .orElseThrow(() -> new OrderNotFoundException(id));   // ✅ propagates to advice
    }
}
```

### Validation on input

Use Bean Validation on the request body — the advice maps the failure automatically:

```java
public record OrderRequest(
    @NotBlank String userId,
    @NotEmpty @Valid List<@NotNull OrderItem> items,
    String couponCode
) {}

@PostMapping("/orders")
public ResponseEntity<Void> place(@Valid @RequestBody OrderRequest req) { ... }
```

### Incorrect

Catching in the controller:

```java
// ❌ every controller repeats this; inconsistent status codes; leaks trace
@GetMapping("/orders/{id}")
public ResponseEntity<?> get(@PathVariable Long id) {
    try {
        return ResponseEntity.ok(orderService.get(id));
    } catch (Exception e) {
        return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
    }
}
```

Returning a raw exception:

```java
// ❌ Jackson can't serialize the exception cleanly; leaks internals
@GetMapping("/orders/{id}")
public Order get(@PathVariable Long id) {
    throw new OrderNotFoundException(id);   // no advice → Spring's default HTML error page
}
```

Letting checked exceptions escape the service without mapping:

```java
// ❌ maps to generic 500 with no context
public Order importFromFile(Path p) throws IOException {
    Files.readAllBytes(p);  // IOException → 500, no ProblemDetail
}
```

Wrap or map it: either catch in the service and rethrow as a domain exception, or add an `@ExceptionHandler(IOException.class)` mapping.

### Context

- **Order of handlers**: Spring picks the most specific `@ExceptionHandler` for the thrown type. Put the catch-all `Exception.class` handler last; it can't be overridden by specificity alone if a more specific handler exists.
- **Async exceptions**: `@RestControllerAdvice` does NOT catch exceptions thrown from `@Async` methods or `CompletableFuture` chains. Handle those inside the async boundary or via `AsyncUncaughtExceptionHandler`.
- **Spring 6 ProblemDetail** is the modern path. Pre-3.x you'd hand-roll an `ErrorResponse` record — still fine, but ProblemDetail is the convention going forward.
- **Cross-ref**: traceId/MDC setup relates to `spring-boot/sb-actuator-health.md` observability; validation patterns also appear in input DTOs in `spring-boot/sb-project-structure.md`.
