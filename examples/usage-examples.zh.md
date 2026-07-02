# 使用示例

安装 skill 后，可以把下面的 prompt 直接粘贴到 Claude Code / Codex / OpenCode / ZCode 里。每个示例都展示了 skill **加载后** Agent 实际会做的事。

Skill 通过 `description` 字段的关键词自动触发 —— 你**不需要**明说"Java"，也不需要引用任何文件名。

[English](./usage-examples.md) | **中文**

---

## 示例 1 —— 编写 Spring Boot 服务（方向 A）

**你输入：**

> 帮我写一个 OrderService，要保存订单、调用支付，订单金额不能超过库存上限

**发生的过程：**

1. Skill 因 "Service" + "保存订单" 触发。
2. Agent 读取 `spring-boot/sb-dependency-injection.md` → 用**构造器注入 + `@RequiredArgsConstructor`**（不是字段 `@Autowired`）。
3. Agent 读取 `spring-boot/sb-mybatis-plus.md` → 继承 `ServiceImpl`，写方法上加 `@Transactional(rollbackFor = Exception.class)`。
4. Agent 读取 `spring-boot/sb-config-profiles.md` → 金额上限从 `@ConfigurationProperties` 取，而不是写死魔法值。

**你得到的结果**（节选）：

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order>
        implements OrderService {

    private final OrderProperties props;        // 类型安全的配置，不是 @Value
    private final PaymentClient paymentClient;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Order placeOrder(OrderRequest request) {
        if (request.amount().compareTo(props.maxAmount()) > 0) {
            throw new OrderAmountExceededException(props.maxAmount());
        }
        Order order = buildOrder(request);
        save(order);                            // ServiceImpl#save，同一事务
        paymentClient.charge(request);          // 同一事务，一起回滚
        return order;
    }
}
```

如果没有 skill，模型可能写出字段 `@Autowired` 注入、用 `@Value` 取上限、漏掉 `@Transactional`。Skill 把它引导到项目约定的写法。

---

## 示例 2 —— 代码审查（方向 B）

**你输入：**

> 审查这个方法的线程安全：
> ```java
> private Map<Long, Order> cache = new HashMap<>();
> public Order get(Long id) {
>     return cache.computeIfAbsent(id, this::load);
> }
> ```

**发生的过程：**

1. Skill 因 "线程安全" 触发。
2. Agent 读取 `code-review/cr-concurrency.md` → 识别出跨线程共享的可变 `HashMap`。
3. Agent 读取 `code-review/cr-anti-patterns.md` → 标出字段没加 `final`。

**你得到的结果：**

> ⚠ **竞态条件** —— 并发 `computeIfAbsent` 下 `HashMap` 会丢更新，扩容时甚至可能死循环。两个调用者同时进 `get()` 会把 map 改坏。
>
> **修复：** 改用线程安全 Map，字段加 final：
> ```java
> private final Map<Long, Order> cache = new ConcurrentHashMap<>();
> ```
>
> 如果还需要容量上限和过期淘汰，用 `Caffeine`：
> ```java
> private final Cache<Long, Order> cache = Caffeine.newBuilder()
>         .maximumSize(10_000)
>         .build();
> ```

Skill 把一句模糊的"审查一下"变成了结构化的清单检查（`cr-concurrency.md` 里有专门的检查清单）。

---

## 示例 3 —— 测试搭建（方向 C）

**你输入：**

> 用 Testcontainers 配 MySQL，测我的 OrderMapper

**发生的过程：**

1. Skill 因 "Testcontainers" + "Mapper" 触发。
2. Agent 读取 `testing/test-testcontainers.md` → 用 `@ServiceConnection`（Spring Boot 3.1+），而不是冗长的老式 `@DynamicPropertySource`。
3. Agent 读取 `testing/test-layering.md` → 把它定位为集成测试，不是单元测试（Mapper 测试必须有真实 DB）。

**你得到的结果：**

```java
@SpringBootTest
@Testcontainers
class OrderMapperTest {

    @Container
    @ServiceConnection                                  // 自动注入 url/user/pass
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8")
            .withReuse(true);                           // 加速重复运行

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

没有 skill 时，模型常常会用 H2（这会掩盖 MySQL 特有的 SQL 问题）或冗长的 `@DynamicPropertySource` 样板代码。

---

## 示例 4 —— 线上排障（方向 D）

**你输入：**

> 线上 OOM 了，怎么排查？服务跑了几小时就挂

**发生的过程：**

1. Skill 因 "OOM" + "线上" 触发。
2. Agent 读取 `jvm/jvm-oom-analysis.md` → 走诊断流程。

**你得到的结果：**

> 首先，如果还没配置，**让下次崩溃时自动抓堆 dump**：
>
> ```
> -XX:+HeapDumpOnOutOfMemoryError
> -XX:HeapDumpPath=/var/log/app/oom-%p.hprof
> ```
>
> 然后**按 OOM 报错信息分类** —— 不同类型修复方式完全不同：
>
> | 报错 | 原因 |
> |------|------|
> | `Java heap space` | 堆泄漏 或 工作集过大 |
> | `Metaspace` | 类加载器泄漏 |
> | `Direct buffer memory` | NIO `ByteBuffer.allocateDirect` 没释放 |
>
> 用 **Eclipse MAT** 打开 `.hprof`，看 **Dominator Tree（支配树）**，按 Retained Heap 排序。最上面的对象就是泄漏源。右键 → *Path to GC Roots* 找出谁在持有它。
>
> 常见泄漏排查：无淘汰策略的静态缓存、没有 `remove()` 的 `ThreadLocal`、忘了反注册的监听器、一次性加载到内存的超大结果集。
>
> 完整步骤见 `jvm/jvm-oom-analysis.md`。

Skill 给出的是结构化的排障手册，而不是泛泛的通用建议。

---

## 触发关键词

Skill 会在以下任意关键词出现时自动加载（来自 SKILL.md 的 `description`）：

- **Spring Boot**：`@RestController`、`@Service`、`@Repository`、`@Configuration`、`@SpringBootApplication`、`@TableName`、`@TableId`、`LambdaQueryWrapper`
- **测试**：`JUnit 5`、`Mockito`、`AssertJ`、`Testcontainers`、`@SpringBootTest`、`@WebMvcTest`、`@DataJpaTest`
- **代码审查**：`concurrency`、`thread safety`、`NPE`、`Optional`、`equals/hashCode`、`Stream`
- **JVM**：`GC tuning`、`OOM`、`thread dump`、`deadlock`、`high CPU`、`heap dump`
- **通用**：`Java`、`JVM`、`MyBatis-Plus`、`JPA`、`Maven`、`pom.xml`、`@Autowired`、`Lombok`、`jakarta.*`、`javax.*`

如果某个 prompt 没触发，但你确实想强制加载，可以用你所用工具的 skill 调用命令（比如 ZCode 里 `/skill java-development <prompt>`）。
