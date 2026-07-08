# Usage Examples

Real prompts you can paste into Claude Code / Codex / OpenCode / ZCode once the
skill is installed. Each shows what the agent does **with** the skill loaded.

The skill triggers automatically from the `description` keywords — you don't
need to mention "Java" explicitly or name any file.

**English** | [中文](./usage-examples.zh.md)

---

## Example 1 — Writing a Spring Boot service (Domain A)

**You type:**

> 帮我写一个 OrderService，要保存订单、调用支付，订单金额不能超过库存上限

**What happens:**

1. Skill triggers on "Service" + "保存订单" (Chinese for "save order").
2. Agent reads `spring-boot/sb-dependency-injection.md` → writes it with
   **constructor injection + `@RequiredArgsConstructor`** (not field `@Autowired`).
3. Agent reads `spring-boot/sb-mybatis-plus.md` → extends `ServiceImpl`,
   uses `@Transactional(rollbackFor = Exception.class)` on the write method.
4. Agent reads `spring-boot/sb-config-profiles.md` → pulls the max-amount limit
   from `@ConfigurationProperties`, not a hardcoded magic number.

**Result you get** (excerpt):

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order>
        implements OrderService {

    private final OrderProperties props;        // typed config, not @Value
    private final PaymentClient paymentClient;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Order placeOrder(OrderRequest request) {
        if (request.amount().compareTo(props.maxAmount()) > 0) {
            throw new OrderAmountExceededException(props.maxAmount());
        }
        Order order = buildOrder(request);
        save(order);                            // ServiceImpl#save, same tx
        paymentClient.charge(request);          // same tx, rolls back together
        return order;
    }
}
```

Without the skill, the model might write `@Autowired` field injection, a raw
`@Value` for the limit, and forget `@Transactional`. The skill steers it to the
project's conventions.

---

## Example 2 — Code review (Domain B)

**You type:**

> Review this method for thread safety:
> ```java
> private Map<Long, Order> cache = new HashMap<>();
> public Order get(Long id) {
>     return cache.computeIfAbsent(id, this::load);
> }
> ```

**What happens:**

1. Skill triggers on "thread safety".
2. Agent reads `code-review/cr-concurrency.md` → recognizes the shared mutable
   `HashMap` across threads.
3. Agent reads `code-review/cr-anti-patterns.md` → flags the non-`final` field.

**Result you get:**

> ⚠ **Race condition** — `HashMap` under concurrent `computeIfAbsent` can lose
> updates or infinite-loop on resize. Two callers hitting `get()` simultaneously
> will corrupt the map.
>
> **Fix:** use a thread-safe map and make the field final:
> ```java
> private final Map<Long, Order> cache = new ConcurrentHashMap<>();
> ```
>
> Or, if you need bounded eviction, use `Caffeine`:
> ```java
> private final Cache<Long, Order> cache = Caffeine.newBuilder()
>         .maximumSize(10_000)
>         .build();
> ```

The skill turns a vague "review this" into a structured checklist pass
(`code-review/cr-concurrency.md` has an explicit checklist).

---

## Example 3 — Test setup (Domain C)

**You type:**

> 用 Testcontainers 配 MySQL，测我的 OrderMapper

**What happens:**

1. Skill triggers on "Testcontainers" + "Mapper".
2. Agent reads `testing/test-testcontainers.md` → uses `@ServiceConnection`
   (Spring Boot 3.1+) instead of the old verbose `@DynamicPropertySource`.
3. Agent reads `testing/test-layering.md` → keeps it as an integration test,
   not a unit test (Mapper tests need a real DB).

**Result you get:**

```java
@SpringBootTest
@Testcontainers
class OrderMapperTest {

    @Container
    @ServiceConnection                                  // auto-wires url/user/pass
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8")
            .withReuse(true);                           // fast re-runs

    @Autowired OrderMapper orderMapper;

    @Test
    void insertsAndSelects() {
        Order o = new Order();
        o.setUserId("u1");
        o.setStatus("CREATED");
        orderMapper.insert(o);

        Order found = orderMapper.selectById(o.getId());
        assertThat(found.getUserId()).isEqualTo("u1");
    }
}
```

Without the skill, the model often reaches for H2 (which hides MySQL-specific
SQL bugs) or the verbose `@DynamicPropertySource` boilerplate.

---

## Example 4 — Production troubleshooting (Domain D)

**You type:**

> 线上 OOM 了，怎么排查？服务跑了几小时就挂

**What happens:**

1. Skill triggers on "OOM" + "线上" (production).
2. Agent reads `jvm/jvm-oom-analysis.md` → walks the diagnostic flow.

**Result you get:**

> First, **capture a heap dump automatically on the next crash** if you haven't:
>
> ```
> -XX:+HeapDumpOnOutOfMemoryError
> -XX:HeapDumpPath=/var/log/app/oom-%p.hprof
> ```
>
> Then **classify by the OOM message** — the fix differs per type:
>
> | Message | Cause |
> |---------|-------|
> | `Java heap space` | Heap leak or too-large working set |
> | `Metaspace` | Class-loader leak |
> | `Direct buffer memory` | NIO `ByteBuffer.allocateDirect` not released |
>
> Open the `.hprof` in **Eclipse MAT** and look at the **Dominator Tree**
> (sort by Retained Heap). The top retainer is the leak source. Right-click →
> *Path to GC Roots* to find what's holding it.
>
> Common leaks to check: static cache without eviction, `ThreadLocal` without
> `remove()`, listeners never deregistered, huge result sets loaded in memory.
>
> See `jvm/jvm-oom-analysis.md` for the full step-by-step.

The skill gives a structured playbook instead of generic advice.

---

## Trigger keywords

The skill auto-loads on any of these (from the SKILL.md `description`):

- **Spring Boot**: `@RestController`, `@Service`, `@Repository`, `@Configuration`,
  `@SpringBootApplication`, `@TableName`, `@TableId`, `LambdaQueryWrapper`
- **Testing**: `JUnit 5`, `Mockito`, `AssertJ`, `Testcontainers`, `@SpringBootTest`,
  `@WebMvcTest`, `@DataJpaTest`
- **Code review**: `concurrency`, `thread safety`, `NPE`, `Optional`,
  `equals/hashCode`, `Stream`
- **JVM**: `GC tuning`, `OOM`, `thread dump`, `deadlock`, `high CPU`, `heap dump`
- **General**: `Java`, `JVM`, `MyBatis-Plus`, `JPA`, `Maven`, `pom.xml`,
  `@Autowired`, `Lombok`, `jakarta.*`, `javax.*`

If a prompt doesn't trigger and you want to force-load it, use your tool's
skill-invocation command (e.g. `/skill java-development <prompt>` in ZCode).
