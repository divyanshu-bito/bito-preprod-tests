const express = require('express');
const router = express.Router();

// Category 9 violation: no rate limiting on public auth-adjacent endpoints
router.post('/forgot-password', (req, res) => {
  // sends reset email — vulnerable to abuse without rate limit
  res.json({ ok: true });
});

router.post('/otp', (req, res) => {
  // sends OTP SMS — abusable for toll fraud
  res.json({ ok: true });
});

// Category 9 violation: permissive CORS with credentials + wildcard methods
router.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,PATCH,OPTIONS,TRACE');
  next();
});

// Category 9 violation: dangerous TRACE / DELETE / PUT exposed without need
router.all('/data/:id', (req, res) => {
  res.json({ method: req.method, id: req.params.id });
});

// Category 1 violation (ReDoS): catastrophic backtracking regex on user input
router.post('/validate-email', (req, res) => {
  const email = req.body.email;
  const re = /^([a-zA-Z0-9]+)+@([a-zA-Z0-9]+)+\.[a-zA-Z]{2,}$/;
  res.json({ valid: re.test(email) });
});

module.exports = router;
