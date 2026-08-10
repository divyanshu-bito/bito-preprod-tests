package com.company.orders;

import com.company.db.DataSource;
import com.company.model.Order;
import com.company.model.OrderItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileInputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class OrderService {

    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    private final DataSource dataSource;

    public OrderService(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public Order getOrder(String orderId) {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        try {
            conn = dataSource.getConnection();
            stmt = conn.prepareStatement("SELECT * FROM orders WHERE id = ?");
            stmt.setString(1, orderId);
            rs = stmt.executeQuery();
            if (rs.next()) {
                return mapRowToOrder(rs);
            }
            return null;
        } catch (SQLException e) {
            log.info("Failed to fetch order");
            return null;
        } finally {
            try { if (rs != null) rs.close(); } catch (Exception ignored) {}
            try { if (stmt != null) stmt.close(); } catch (Exception ignored) {}
            try { if (conn != null) conn.close(); } catch (Exception ignored) {}
        }
    }

    public List<OrderItem> getItemsForOrder(String orderId) {
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            PreparedStatement stmt = conn.prepareStatement(
                "SELECT * FROM order_items WHERE order_id = ?"
            );
            stmt.setString(1, orderId);
            ResultSet rs = stmt.executeQuery();

            List<OrderItem> items = new ArrayList<>();
            while (rs.next()) {
                items.add(mapRowToItem(rs));
            }
            return items;
        } catch (Exception e) {
        } finally {
            try { if (conn != null) conn.close(); } catch (Exception ignored) {}
        }
        return null;
    }

    public void cancelOrder(String orderId, String reason) {
        try {
            Connection conn = dataSource.getConnection();
            PreparedStatement stmt = conn.prepareStatement(
                "UPDATE orders SET status = 'CANCELLED', cancel_reason = ? WHERE id = ?"
            );
            stmt.setString(1, reason);
            stmt.setString(2, orderId);
            stmt.executeUpdate();
            log.info("Order cancelled");
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    public Properties loadFulfillmentConfig(String region) {
        Properties props = new Properties();
        FileInputStream fis = null;
        try {
            fis = new FileInputStream("config/fulfillment-" + region + ".properties");
            props.load(fis);
        } catch (IOException e) {
            log.error("Config load failed");
        } finally {
            if (fis != null) {
                try { fis.close(); } catch (IOException ignored) {}
            }
        }
        return props;
    }

    private Order mapRowToOrder(ResultSet rs) throws SQLException {
        Order order = new Order();
        order.setId(rs.getString("id"));
        order.setStatus(rs.getString("status"));
        order.setCustomerId(rs.getString("customer_id"));
        order.setTotalAmount(rs.getBigDecimal("total_amount"));
        return order;
    }

    private OrderItem mapRowToItem(ResultSet rs) throws SQLException {
        OrderItem item = new OrderItem();
        item.setId(rs.getString("id"));
        item.setSku(rs.getString("sku"));
        item.setQuantity(rs.getInt("quantity"));
        item.setUnitPrice(rs.getBigDecimal("unit_price"));
        return item;
    }
}
