---
title: MyBatis-Plus Best Practices (Default Persistence Layer)
impact: HIGH
impactDescription: MyBatis-Plus is the China mainstream; correct usage avoids SQL injection, pagination bugs, and Lombok-equals traps
tags: mybatis-plus, mybatis, persistence, basemapper, iservice, lambda-query, pagination, logical-delete
description: Use BaseMapper/IService with LambdaQueryWrapper, configure pagination + logical delete plugins, prefer LambdaQuery to avoid column-name typos
---

## MyBatis-Plus Best Practices (Default Persistence Layer)

MyBatis-Plus (MP) is the default persistence layer in this skill — it's the dominant choice in Chinese Spring Boot projects. It augments raw MyBatis with CRUD generation, query wrappers, and plugins without the abstraction weight of JPA/Hibernate.

### Why it matters

- **Less boilerplate**: `BaseMapper` generates single-table CRUD; `IService` adds batch ops. No hand-written XML for simple cases.
- **Type-safe queries**: `LambdaQueryWrapper` references methods (`Order::getStatus`) instead of column-name strings — renames are caught at compile time, not runtime.
- **Built-in plugins**: pagination, logical delete, optimistic lock, and auto-fill come as one-line config — but **must be configured**, otherwise pagination silently returns all rows.
- **Composable with raw MyBatis**: complex queries still go to XML mappers; MP doesn't lock you in.

### Dependency + config

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.7</version>
</dependency>
<!-- SB2.x uses: mybatis-plus-boot-starter (without the 'spring-boot3' suffix) -->
```

**Critical**: register the pagination + optimistic-lock interceptor, else `Page` returns the full result set:

```java
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
        return interceptor;
    }
}
```

### Entity with annotations

```java
@Data                                          // Lombok @Data OK on @TableName entities (no lazy proxy like JPA)
@TableName("t_order")
public class Order {
    @TableId(type = IdType.ASSIGN_ID)          // snowflake ID by default; use AUTO for DB auto-increment
    private Long id;

    private String orderNo;

    private Long userId;

    private BigDecimal amount;

    @TableField(fill = FieldFill.INSERT)       // auto-filled on insert
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)// auto-filled on insert and update
    private LocalDateTime updateTime;

    @TableLogic                                // logical delete: deleted=1 means removed
    @TableField(select = false)                // not selected by default in normal queries
    private Integer deleted;

    @Version                                   // optimistic lock
    private Integer version;
}
```

### Mapper + Service layers

```java
public interface OrderMapper extends BaseMapper<Order> {
    // single-table CRUD inherited. Complex queries go to XML or @Select.
    @Select("SELECT * FROM t_order WHERE user_id = #{userId} AND status = 'PAID'")
    List<Order> findPaidByUser(@Param("userId") Long userId);
}

@Service
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order> implements OrderService {
    // inherits IService: saveBatch, removeById, getOne, page, lambdaQuery(), etc.
}
```

### Prefer LambdaQueryWrapper over string columns

```java
// ✅ LambdaQuery — type-safe, refactor-friendly
List<Order> orders = orderService.lambdaQuery()
        .eq(Order::getUserId, userId)
        .ge(Order::getAmount, BigDecimal.valueOf(100))
        .orderByDesc(Order::getCreateTime)
        .list();

// ❌ string column name — typo-prone, breaks silently on rename
QueryWrapper<Order> w = new QueryWrapper<>();
w.eq("user_id", userId)
 .ge("amount", 100);
```

Use `QueryWrapper` (string-based) only for dynamic SQL where columns are themselves dynamic; otherwise always `LambdaQueryWrapper`.

### Pagination

```java
Page<Order> page = new Page<>(1, 20);         // current=1, size=20
Page<Order> result = orderService.page(page,
        Wrappers.<Order>lambdaQuery().eq(Order::getStatus, "PAID"));

result.getRecords();    // List<Order>
result.getTotal();      // long total count
result.getPages();      // total pages
```

**Pitfall**: if you forget the `PaginationInnerInterceptor`, `page.getRecords()` returns **all** rows and `getTotal()` returns the full count — silent correctness bug. Always verify with a known-large dataset in tests.

### Logical delete

With `@TableLogic`, `removeById`/`remove` issue `UPDATE ... SET deleted=1` instead of `DELETE`. Queries automatically append `AND deleted=0`. Two caveats:

1. **Unique key conflicts**: a soft-deleted row still occupies a unique index. If `order_no` is unique, re-inserting the same `order_no` after soft delete fails. Either include `deleted` in the unique index or use a non-unique business key.
2. **Bypassing the filter**: queries you write in raw XML `@Select` do **not** get the `deleted=0` predicate automatically — add it yourself.

### Auto-fill handler

```java
@Component
public class MetaObjectHandlerImpl implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

### @Transactional still applies

MP's `IService` methods are not transactional by default. Wrap multi-write operations:

```java
@Service
@RequiredArgsConstructor
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order> implements OrderService {
    private final InventoryClient inventoryClient;

    @Transactional(rollbackFor = Exception.class)
    public void placeOrder(OrderRequest req) {
        save(buildOrder(req));
        inventoryClient.decrement(req.items());
    }
}
```

Same transaction caveats as JPA: self-invocation bypasses the proxy, checked exceptions don't roll back without `rollbackFor`. See `spring-boot/sb-jpa-repository.md` § "@Transactional placement" (the rules are framework-agnostic).

### Code generation

Don't hand-write entities for existing tables — use the generator to scaffold:

```java
FastAutoGenerator.create("jdbc:mysql://localhost:3306/shop", "root", "pass")
        .globalConfig(b -> b.author("shop-team").outputDir("src/main/java").dateType(DateType.TIME_PACK))
        .packageConfig(b -> b.parent("com.acme.shop").pathInfo(Collections.singletonMap(
                OutputFile.xml, "src/main/resources/mapper")))
        .strategyConfig(b -> b.addInclude("t_order","t_order_item").addTablePrefix("t_"))
        .execute();
```

Generates Entity/Mapper/Mapper.xml/Service/ServiceImpl/Controller. Delete what you don't need; the entity is the useful part.

### Incorrect

String-column queries everywhere:

```java
// ❌ typo "user_idd" compiles, fails at runtime
orderService.list(new QueryWrapper<Order>().eq("user_idd", userId));
```

Forgetting the pagination interceptor:

```java
// ❌ page 1 size 20 returns 10000 rows silently
Page<Order> p = orderService.page(new Page<>(1, 20));
```

`@Data` on entities without considering equals:

MP entities don't have the lazy-proxy problem JPA entities do, so `@Data` is generally safe. But beware `equals`/`hashCode` on `id=null` before insert (two unsaved entities "equal"). If you put entities in a `Set` before saving, override `equals` to guard null id — see `code-review/cr-equals-hashcode.md`.

### When to use raw MyBatis XML instead

- Multi-table joins with complex result mapping (`<resultMap>` with `<collection>`)
- Reports with heavily dynamic SQL (`<if>`, `<foreach>`, `<choose>`)
- Performance-critical queries where you want full SQL control

MP and raw MyBatis coexist cleanly — put simple CRUD on `BaseMapper`, complex queries in XML mappers.

### Context

- **SB3 vs SB2 starter**: the artifact id differs — `mybatis-plus-spring-boot3-starter` for SB3, `mybatis-plus-boot-starter` for SB2. Using the wrong one fails to autoconfigure. See `spring-boot/sb-migration-2-to-3.md`.
- **DbType**: set `DbType` correctly in `PaginationInnerInterceptor` (MYSQL, POSTGRE_SQL, ORACLE...) — wrong dialect generates invalid `LIMIT` syntax.
- **Cross-ref**: transaction rules shared with `spring-boot/sb-jpa-repository.md`; equals/hashCode in `code-review/cr-equals-hashcode.md`; for OSS/foreign contexts JPA is covered in `spring-boot/sb-jpa-repository.md`.
