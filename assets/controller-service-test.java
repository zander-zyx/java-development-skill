// =============================================================================
// Controller + Service + Mapper + Entity + DTO + Test skeleton.
// MyBatis-Plus default persistence layer, Spring Boot 3.x (jakarta).
// Split these into the package structure shown in sb-project-structure.md.
// =============================================================================

// ---------- com/acme/shop/order/dto/OrderRequest.java ----------
package com.acme.shop.order.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.util.List;

public record OrderRequest(
        @NotBlank String userId,
        @NotEmpty List<OrderItem> items,
        String couponCode,
        @NotNull BigDecimal amount
) {
    public record OrderItem(@NotBlank String sku, int qty) {}
}


// ---------- com/acme/shop/order/dto/OrderResponse.java ----------
package com.acme.shop.order.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record OrderResponse(Long id, String userId, BigDecimal amount, String status, LocalDateTime createdAt) {}


// ---------- com/acme/shop/order/Order.java (entity) ----------
package com.acme.shop.order;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("t_order")
public class Order {
    @TableId(type = IdType.ASSIGN_ID)              // snowflake
    private Long id;
    private String userId;
    private BigDecimal amount;
    private String status;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableLogic
    @TableField(select = false)
    private Integer deleted;
}


// ---------- com/acme/shop/order/OrderMapper.java ----------
package com.acme.shop.order;

import com.acme.shop.order.Order;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface OrderMapper extends BaseMapper<Order> {
    // single-table CRUD inherited; complex queries go to resources/mapper/OrderMapper.xml
}


// ---------- com/acme/shop/order/OrderService.java ----------
package com.acme.shop.order;

import com.acme.shop.order.dto.OrderRequest;
import com.acme.shop.order.dto.OrderResponse;

public interface OrderService {
    OrderResponse placeOrder(OrderRequest request);
    OrderResponse getOrder(Long id);
}


// ---------- com/acme/shop/order/OrderServiceImpl.java ----------
package com.acme.shop.order;

import com.acme.shop.order.dto.OrderRequest;
import com.acme.shop.order.dto.OrderResponse;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order> implements OrderService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public OrderResponse placeOrder(OrderRequest request) {
        log.info("Placing order for user={}", request.userId());
        Order order = new Order();
        order.setUserId(request.userId());
        order.setAmount(request.amount());
        order.setStatus("CREATED");
        save(order);                                // inherited from ServiceImpl
        return toResponse(order);
    }

    @Override
    public OrderResponse getOrder(Long id) {
        Order order = getById(id);                  // throws if not found via MP's behavior; or use lambdaQuery
        if (order == null) {
            throw new com.acme.shop.common.OrderNotFoundException(id);
        }
        return toResponse(order);
    }

    private OrderResponse toResponse(Order o) {
        return new OrderResponse(o.getId(), o.getUserId(), o.getAmount(), o.getStatus(), o.getCreateTime());
    }
}


// ---------- com/acme/shop/order/OrderController.java ----------
package com.acme.shop.order;

import com.acme.shop.order.dto.OrderRequest;
import com.acme.shop.order.dto.OrderResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URI;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Slf4j
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    public ResponseEntity<OrderResponse> place(@Valid @RequestBody OrderRequest request) {
        OrderResponse created = orderService.placeOrder(request);
        return ResponseEntity.created(URI.create("/api/orders/" + created.id())).body(created);
    }

    @GetMapping("/{id}")
    public OrderResponse get(@PathVariable Long id) {
        return orderService.getOrder(id);
    }
}


// ---------- src/test/java/.../OrderServiceTest.java (unit, no Spring) ----------
package com.acme.shop.order;

import com.acme.shop.order.dto.OrderRequest;
import com.acme.shop.order.dto.OrderResponse;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    OrderMapper orderMapper;

    @InjectMocks
    OrderServiceImpl service;

    @Test
    void placesOrderWithCreatedStatus() {
        // given
        var req = new OrderRequest("u1", java.util.List.of(), null, BigDecimal.TEN);
        when(orderMapper.insert(any(Order.class))).thenAnswer(inv -> {
            ((Order) inv.getArgument(0)).setId(1L);
            return 1;
        });

        // when
        OrderResponse resp = service.placeOrder(req);

        // then
        assertThat(resp.status()).isEqualTo("CREATED");
        assertThat(resp.id()).isEqualTo(1L);
    }
}
