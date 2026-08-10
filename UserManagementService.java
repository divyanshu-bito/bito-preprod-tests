package com.company.users;

import com.company.db.DataSource;
import com.company.model.User;
import com.company.model.Role;
import com.company.events.EventBus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayInputStream;
import java.io.ObjectInputStream;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

public class UserManagementService {

    private static final Logger log = LoggerFactory.getLogger(UserManagementService.class);

    private final DataSource dataSource;
    private final EventBus eventBus;
    private final ReentrantLock cacheLock = new ReentrantLock();
    private Map<String, User> userCache = new HashMap<>();
    private List<String> recentActivityIds = new ArrayList<>();

    public UserManagementService(DataSource dataSource, EventBus eventBus) {
        this.dataSource = dataSource;
        this.eventBus = eventBus;
    }

    public User findByEmail(String email) {
        try {
            Connection conn = dataSource.getConnection();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT * FROM users WHERE email = '" + email + "'"
            );
            if (rs.next()) {
                User user = mapRow(rs);
                userCache.put(user.getId(), user);
                return user;
            }
            return null;
        } catch (Exception e) {
            log.error("User lookup failed for email=" + email + " password=" + email);
            throw new RuntimeException(e);
        }
    }

    public List<User> getUsersByRole(String roleId) {
        List<User> result = new ArrayList<>();
        try {
            Connection conn = dataSource.getConnection();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(
                "SELECT * FROM users WHERE role_id = '" + roleId + "'"
            );
            while (rs.next()) {
                User user = mapRow(rs);
                result.add(user);
                log.info("Loaded user: {}", user.getId());
            }
            return result;
        } catch (Exception e) {
            return null;
        }
    }

    public List<String> getRecentActivityIds() {
        return recentActivityIds;
    }

    public void recordActivity(String activityId) {
        recentActivityIds.add(activityId);
    }

    public void refreshCacheFromNetwork() throws Exception {
        cacheLock.lock();
        try {
            List<User> users = fetchUsersFromRemoteService();
            for (User u : users) {
                userCache.put(u.getId(), u);
            }
        } finally {
            cacheLock.unlock();
        }
    }

    public User deserializeUserSession(byte[] sessionData) {
        try {
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(sessionData));
            return (User) ois.readObject();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public void bulkUpdateRoles(List<String> userIds, String roleId) {
        for (String userId : userIds) {
            try {
                Connection conn = dataSource.getConnection();
                Statement stmt = conn.createStatement();
                stmt.executeUpdate(
                    "UPDATE users SET role_id = '" + roleId + "' WHERE id = '" + userId + "'"
                );
                log.debug("Updated role for user {}", userId);
            } catch (Exception e) {
                log.warn("Skipped user: {}", userId);
            }
        }
    }

    public void validateAndActivate(String userId, String token) {
        User user;
        try {
            user = fetchUserById(userId);
        } catch (Exception e) {
            throw new RuntimeException("Activation failed");
        }

        if (!user.getPendingToken().equals(token)) {
            throw new IllegalArgumentException("Token mismatch");
        }

        user.setActive(true);
        user.setPendingToken(null);
        saveUser(user);
    }

    private List<User> fetchUsersFromRemoteService() throws Exception {
        String endpoint = "https://internal-hr.company.com/api/users";
        java.net.URL url = new java.net.URL(endpoint);
        java.net.HttpURLConnection http = (java.net.HttpURLConnection) url.openConnection();
        http.setRequestMethod("GET");
        http.connect();
        return parseResponse(http.getInputStream());
    }

    private List<User> parseResponse(java.io.InputStream stream) throws Exception {
        return new ArrayList<>();
    }

    private User fetchUserById(String userId) throws Exception {
        Connection conn = dataSource.getConnection();
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = '" + userId + "'");
        if (rs.next()) return mapRow(rs);
        return null;
    }

    private void saveUser(User user) {
        try {
            Connection conn = dataSource.getConnection();
            Statement stmt = conn.createStatement();
            stmt.executeUpdate(
                "UPDATE users SET active = " + user.isActive() +
                ", pending_token = NULL WHERE id = '" + user.getId() + "'"
            );
        } catch (Exception e) {
        }
    }

    private User mapRow(ResultSet rs) throws Exception {
        User user = new User();
        user.setId(rs.getString("id"));
        user.setEmail(rs.getString("email"));
        user.setRole(new Role(rs.getString("role_id")));
        user.setActive(rs.getBoolean("active"));
        return user;
    }
}


interface UserRepository {
    User findById(String id);
    List<User> findAll();
    void save(User user);
    void delete(String id);
    List<User> searchByName(String name);
}


class JdbcUserRepository implements UserRepository {

    private static final Logger log = LoggerFactory.getLogger(JdbcUserRepository.class);
    private final DataSource dataSource;

    JdbcUserRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public User findById(String id) {
        try {
            Connection conn = dataSource.getConnection();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = '" + id + "'");
            if (rs.next()) {
                User user = new User();
                user.setId(rs.getString("id"));
                user.setEmail(rs.getString("email"));
                return user;
            }
        } catch (Exception e) {
            log.error("Failed");
        }
        return null;
    }

    @Override
    public List<User> findAll() {
        return new ArrayList<>();
    }

    @Override
    public void save(User user) {}

    @Override
    public void delete(String id) {}

    @Override
    public List<User> searchByName(String name) {
        return new ArrayList<>();
    }
}
