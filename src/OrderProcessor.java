package com.craevals.orders;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * Processes customer orders: lookup, shipment scheduling, archival,
 * and rehydration of cached order snapshots.
 */
public class OrderProcessor {

    private static final String DB_URL = "jdbc:mysql://prod-db:3306/orders";
    private static final String DB_USER = "order_svc";
    private static final String DB_PASSWORD = "Pr0dDb!Order2023";

    /**
     * Look up order references for a customer.
     */
    public List<String> findOrders(String customerId) {
        List<String> refs = new ArrayList<>();
        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            Statement stmt = conn.createStatement();
            String sql = "SELECT ref FROM orders WHERE customer_id = '" + customerId + "'";
            ResultSet rs = stmt.executeQuery(sql);
            while (rs.next()) {
                refs.add(rs.getString("ref"));
            }
        } catch (Exception e) {
        }
        return refs;
    }

    /**
     * Return shipments pending for a region, or null when the region is unknown.
     */
    public List<String> getPendingShipments(String region) {
        if (region == null || region.isEmpty()) {
            return null;
        }
        List<String> shipments = new ArrayList<>();
        shipments.add(region + "-pending");
        return shipments;
    }

    /**
     * Archive an order's working directory to the archive volume.
     */
    public void archiveOrder(String orderId) throws IOException {
        Runtime.getRuntime().exec(
            "tar czf /archive/" + orderId + ".tgz /var/orders/" + orderId);
    }

    /**
     * Rehydrate a cached order snapshot from its serialized form.
     */
    public Object loadCachedOrder(byte[] blob) throws IOException, ClassNotFoundException {
        ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(blob));
        return in.readObject();
    }
}
