---
title: Layered Project Structure
impact: HIGH
impactDescription: A consistent package layout makes code findable and tests easier to write
tags: structure, packages, layers, controller-service-repository
description: Use a layered package structure (controller/service/repository/dto) per bounded context, not per layer
---

## Layered Project Structure

Organize packages **by feature/bounded context** first, then by layer inside. Avoid the "package by layer" style where all controllers live in one folder.

### Why it matters

- **Findability** — when packages are `com.acme.order`, all order-related code is in one place. When they're `com.acme.controller`, a single feature is scattered across four top-level packages.
- **Cohesion over coupling** — code that changes together lives together. A change to "orders" touches controller+service+repo for orders, so co-locate them.
- **Modularization later** — feature packages map cleanly onto Spring Modulith or multi-module Gradle if you later need hard boundaries.

### Correct — package by feature

```
com.acme.shop
├── order
│   ├── OrderController.java          @RestController
│   ├── OrderService.java             @Service
│   ├── OrderRepository.java          extends JpaRepository
│   ├── Order.java                    @Entity
│   ├── dto
│   │   ├── OrderRequest.java         record
│   │   └── OrderResponse.java        record
│   └── event
│       └── OrderPlacedEvent.java     record
├── payment
│   ├── PaymentController.java
│   ├── PaymentService.java
│   └── ...
├── user
│   └── ...
└── config
    ├── SecurityConfig.java           @Configuration
    └── WebConfig.java
```

Within each feature package, layer by class name suffix (`Controller`, `Service`, `Repository`) rather than by sub-package — the layer is obvious from the class and there aren't enough files per layer to justify a sub-package. `dto` and `event` sub-packages are the exceptions, because they collect multiple small types.

### Incorrect — package by layer

```
com.acme.shop
├── controller                        ❌ a feature spread across 4 folders
│   ├── OrderController.java
│   ├── PaymentController.java
│   └── UserController.java
├── service
│   ├── OrderService.java
│   └── ...
├── repository
│   └── ...
└── entity
    └── ...
```

To work on "orders" you'd open 4 folders. To delete an order feature you'd grep through 4 folders. This style doesn't scale past ~20 classes.

### Where things go — quick rules

| Type | Location | Notes |
|------|----------|-------|
| `@RestController` | feature package | Never put business logic here — only HTTP mapping + DTO conversion |
| `@Service` | feature package | Transaction boundary; orchestrates repository + clients |
| `JpaRepository` | feature package | Interface only; no query logic that belongs in service |
| `@Entity` | feature package | Don't leak entities into controller responses — use a DTO/record |
| DTO records | `feature/dto` | Use `record`, never expose entity directly (see `spring-boot/sb-jpa-repository.md`) |
| `@Configuration` | top-level `config` package | One config class per concern (SecurityConfig, WebConfig) |
| Global exception handler | top-level `config` or `web` package | See `spring-boot/sb-exception-handling.md` |
| `main` class | top-level package | `@SpringBootApplication` should sit above feature packages so `@ComponentScan` finds them |

### Main class placement

```java
package com.acme.shop;                  // ← top-level, ABOVE feature packages

@SpringBootApplication
public class ShopApplication {
    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);
    }
}
```

If the main class sits at `com.acme.shop.order`, then `payment.*` beans won't be scanned. Always place it at the root.

### Don't expose entities from controllers

```java
// ❌ leaks JPA entity + lazy-loading trap (N+1, serialization cycles)
@GetMapping("/orders/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderService.find(id);
}

// ✅ returns an explicit DTO
@GetMapping("/orders/{id}")
public OrderResponse getOrder(@PathVariable Long id) {
    return orderService.find(id);       // service returns OrderResponse, not Order
}
```

### Context

- **Small apps** — if the whole app is one feature, package-by-layer is tolerable. The rule of thumb: as soon as you have two features, switch to package-by-feature.
- **Spring Modulith / hexagonal** — if you adopt a stricter architecture (ports & adapters), the same principle applies: group by module/feature, not by technical role.
- **Cross-ref**: DTO conversion and the N+1 trap live in `spring-boot/sb-jpa-repository.md`; exception handling in `spring-boot/sb-exception-handling.md`.
