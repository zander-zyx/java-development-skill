---
title: AssertJ and Coverage
impact: MEDIUM
impactDescription: AssertJ's fluent assertions give readable tests and precise failure messages; coverage measures behavior not lines
tags: assertj, coverage, jacoco, assertions, fluent
description: Use AssertJ for fluent assertions; treat JaCoCo as a floor not a target; cover behavior not lines
alwaysApply: true
---

## AssertJ and Coverage

AssertJ gives you fluent, type-safe assertions with descriptive failure messages. JaCoCo measures line/branch coverage — use it as a floor, not a target.

### AssertJ — prefer over JUnit assertions

```java
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.tuple;

// ✅ AssertJ: fluent, descriptive, chainable
assertThat(orders)
    .isNotEmpty()
    .hasSize(3)
    .extracting(Order::getStatus, Order::getAmount)
    .containsExactly(
        tuple(Status.CREATED, BigDecimal.valueOf(100)),
        tuple(Status.PAID,    BigDecimal.valueOf(200)),
        tuple(Status.SHIPPED, BigDecimal.valueOf(300)));

// Failure message is informative:
// "Expected size: 3 but was: 4 [...]"
```

JUnit's `assertEquals(3, orders.size())` gives "expected 3 but was 4" with no context. AssertJ tells you what the actual values were.

### Common AssertJ patterns

**Collections**:
```java
assertThat(users)
    .extracting(User::getEmail)
    .allSatisfy(email -> assertThat(email).contains("@"))
    .doesNotContain(null);
```

**Exceptions**:
```java
assertThatThrownBy(() -> service.placeOrder(req))
    .isInstanceOf(CartLimitExceededException.class)
    .hasMessageContaining("limit")
    .hasFieldOrPropertyWithValue("limit", 50);
```

**Soft assertions** (run all, report all failures):
```java
@Test
void validatesOrder() {
    SoftAssertions.assertSoftly(softly -> {
        softly.assertThat(order.getStatus()).isEqualTo(Status.CREATED);
        softly.assertThat(order.getItems()).hasSize(2);
        softly.assertThat(order.getAmount()).isEqualByComparingTo("100");
    });
}
```
Without soft assertions, the first failure stops the test — you fix one issue per run. Soft assertions report all at once.

**BigDecimal**:
```java
// ✅ compares value, not scale
assertThat(amount).isEqualByComparingTo(BigDecimal.valueOf(100));

// ❌ equals — 100 != 100.00 due to scale
assertThat(amount).isEqualTo(BigDecimal.valueOf(100));
```

**Maps**:
```java
assertThat(map)
    .containsKey("PAID")
    .containsEntry("PAID", expectedOrder)
    .doesNotContainKey("CANCELLED");
```

**Optional / Stream**:
```java
assertThat(orderRepo.findById(1L))
    .isPresent()
    .get()
    .extracting(Order::getStatus)
    .isEqualTo(Status.PAID);
```

**Dates**:
```java
assertThat(localDateTime)
    .isAfter(LocalDateTime.of(2026, 7, 1, 0, 0))
    .isBefore(LocalDateTime.now());
```

### Coverage — a floor, not a target

100% line coverage is not 100% behavior coverage. A method covered by one test that hits every line may still have untested branches and edge cases.

**Use coverage as a floor**:
- Aim for ~80% on business-logic packages.
- Coverage on DTOs/getters is meaningless — exclude them from the report.
- A drop in coverage is a signal — someone added code without tests.

**Don't**:
- Don't chase 100% — you'll write tests that exercise lines without asserting behavior.
- Don't use coverage as a performance metric for developers.
- Don't enable coverage checks on tests themselves.

### JaCoCo setup

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <executions>
        <execution>
            <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals><goal>report</goal></goals>
        </execution>
        <execution>
            <id>check</id>
            <goals><goal>check</goal></goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.70</minimum>   <!-- floor; tune per package -->
                            </limit>
                        </limits>
                    </rule>
                </rules>
                <!-- exclude DTOs, configs, application main -->
                <excludes>
                    <exclude>**/dto/**</exclude>
                    <exclude>**/config/**</exclude>
                    <exclude>**/*Application.*</exclude>
                </excludes>
            </configuration>
        </execution>
    </executions>
</plugin>
```

`mvn test` runs tests with JaCoCo agent; `mvn verify` enforces the coverage check.

### Behavior over lines

```java
// ❌ line-coverage-style test — exercises lines, asserts little
@Test
void test() {
    var result = service.compute(input);
    assertNotNull(result);                              // passes even if result is wrong
}

// ✅ behavior test — asserts the actual computation
@Test
void applies10PercentDiscountForRepeatCustomer() {
    var result = service.compute(repeatCustomerInput);
    assertThat(result.discount()).isEqualByComparingTo("10.00");
}
```

### Review checklist

- [ ] Tests using JUnit `assertEquals` where AssertJ would be clearer?
- [ ] AssertJ assertions that just check `isNotNull` without verifying content?
- [ ] BigDecimal equality via `.isEqualTo` (scale trap) instead of `isEqualByComparingTo`?
- [ ] Coverage gate too high (chasing lines) or absent (no floor)?
- [ ] Coverage on DTOs/config that should be excluded?
- [ ] Tests that pass without meaningful assertion?

### Context

- **AssertJ vs Hamcrest**: AssertJ is the modern default in Spring Boot (`spring-boot-starter-test` bundles it). Hamcrest works but AssertJ's discoverability (autocomplete on chains) makes it more usable.
- **Mutation testing**: tools like PIT (Pitest) verify test quality by mutating production code — if a mutant survives, the test is weak. A step beyond line coverage.
- **Cross-ref**: AssertJ is used throughout the testing files; JUnit integration in `test-junit5.md`.
