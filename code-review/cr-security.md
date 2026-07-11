---
title: Java Security Review
impact: HIGH
impactDescription: Common Java security mistakes expose secrets, enable injection/deserialization attacks, weaken crypto, or create privilege and data-leak incidents
tags: java, security, injection, secrets, crypto, deserialization, validation
description: Review Java code for high-risk security issues including injection, secrets, unsafe deserialization, weak crypto, path traversal, SSRF, and authorization gaps
---

## Java Security Review

Use this for security-sensitive Java changes, dependency upgrades for CVEs, authentication/authorization code, file/network input handling, serialization, crypto, or broad code review.

### Why it matters

Security bugs in Java apps often come from ordinary code paths: string-built SQL, unsafe object deserialization, logs containing secrets, unbounded file paths, SSRF through HTTP clients, and authorization checks only in the UI.

### Checklist

#### Input and injection

- Do not concatenate SQL, JPQL, LDAP, shell, or template expressions from user input.
- Use prepared statements, framework parameter binding, allowlists, and typed query builders.
- Validate file paths after normalization and keep them inside an allowed base directory.

#### Secrets and logging

- Do not hardcode passwords, tokens, private keys, or cloud credentials.
- Do not log credentials, session IDs, access tokens, full authorization headers, or sensitive PII.
- Keep config examples using placeholders, not real-looking secrets.

#### Serialization and parsing

- Avoid native Java deserialization of untrusted input.
- Constrain polymorphic JSON deserialization; do not enable broad default typing for untrusted payloads.
- Bound payload size and parsing depth for XML/JSON when exposed to users.

#### Crypto

- Do not invent crypto protocols.
- Avoid MD5/SHA-1 for security decisions; use modern password hashing for passwords.
- Use secure random sources for tokens and nonces.

#### Network and authorization

- Validate outbound URLs to prevent SSRF; block internal metadata and loopback targets unless explicitly allowed.
- Enforce authorization on the server side for every protected operation.
- Do not trust client-provided user IDs, roles, prices, or ownership fields.

### When NOT to overreach

- Do not rewrite an entire authentication system during an unrelated feature.
- Do not add heavy security dependencies without checking the project's existing security stack.
- Do not mark a finding as exploitable without evidence; state assumptions and required proof.

### Verification

```bash
mvn -q test
./gradlew test
mvn -q org.owasp:dependency-check-maven:check
./gradlew dependencyCheckAnalyze
```

Only run dependency scanners when they are already configured or the user asks; otherwise suggest them as optional verification.

### Context

- Cross-ref resource leaks in `code-review/cr-resource-leak.md`.
- Cross-ref exception handling in `core/java-exception-handling.md`.
- Cross-ref Spring Boot config/secrets in `spring-boot/sb-config-profiles.md` when Spring Boot is in scope.
