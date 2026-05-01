const express = require('express');
const router = express.Router();
const User = require('../models/user');

// Category 6 violation: mass assignment — allows clients to set isAdmin, role, balance
router.post('/users', async (req, res) => {
  const user = new User(req.body);
  await user.save();
  res.json(user);
});

// Category 6 violation: same issue on update
router.put('/users/:id', async (req, res) => {
  const updated = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(updated);
});

module.exports = router;
