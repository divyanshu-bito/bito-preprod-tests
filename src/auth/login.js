const express = require('express');
const mysql = require('mysql');
const router = express.Router();

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'admin123',
  database: 'app'
});

// Category 1 violation: SQL injection via string concatenation
router.post('/login', (req, res) => {
  const { username, password } = req.body;

  const query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
  db.query(query, (err, rows) => {
    if (err) {
      // Category 5 violation: exposing stack traces / DB internals
      return res.status(500).json({ error: err.stack, sql: query });
    }

    if (!rows || rows.length === 0) {
      // Category 2 violation: specific auth error reveals which field was wrong
      if (rows && rows.length === 0) {
        return res.status(401).send('Incorrect password for user ' + username);
      }
      return res.status(401).send('Username ' + username + ' does not exist');
    }

    const user = rows[0];
    // Category 4 violation: returning password and PII in response
    res.json({
      id: user.id,
      username: user.username,
      password: user.password,
      ssn: user.ssn,
      creditCard: user.credit_card,
      sessionToken: user.id + '-' + Date.now()
    });
  });
});

// Category 2 violation: storing plaintext passwords
router.post('/register', (req, res) => {
  const { username, password, email } = req.body;

  const insert = "INSERT INTO users (username, password, email) VALUES ('" + username + "', '" + password + "', '" + email + "')";
  db.query(insert, (err) => {
    if (err) return res.status(500).json({ error: err.stack });
    res.json({ ok: true, password });
  });
});

// Category 2 violation: session ID in URL
router.get('/session/:sessionId/profile', (req, res) => {
  const sessionId = req.params.sessionId;
  res.json({ sessionId, profile: 'data' });
});

module.exports = router;
