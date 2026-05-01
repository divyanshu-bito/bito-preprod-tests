const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const router = express.Router();

// Category 1 violation: command injection via user-controlled data passed to exec
router.get('/ping', (req, res) => {
  const host = req.query.host;
  exec('ping -c 1 ' + host, (err, stdout) => {
    if (err) return res.status(500).json({ error: err.stack });
    res.send(stdout);
  });
});

// Category 1 violation: eval on user input
router.post('/calc', (req, res) => {
  const expression = req.body.expression;
  const result = eval(expression);
  res.json({ result });
});

// Category 3 violation: only checks authentication, not role authorization
router.get('/admin', (req, res) => {
  if (!req.user) {
    return res.status(401).send('Unauthorized');
  }
  res.send('Admin panel - all users data');
});

// Category 3 violation: IDOR — no ownership check on recordId
router.get('/records', (req, res) => {
  const recordId = req.query.recordId;
  const filePath = '/var/data/records/' + recordId + '.json';
  const data = fs.readFileSync(filePath, 'utf-8');
  res.json(JSON.parse(data));
});

// Category 3 violation: no extra authorization for sensitive permission change
router.post('/users/:id/promote', (req, res) => {
  if (!req.user) return res.status(401).send('Unauthorized');
  const targetUserId = req.params.id;
  // promotes any user to admin if requester is merely logged in
  db.query("UPDATE users SET role = 'admin' WHERE id = " + targetUserId);
  res.json({ promoted: targetUserId });
});

module.exports = router;
