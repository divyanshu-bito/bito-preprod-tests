const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: String,
  email: String,
  password: String,
  role: { type: String, default: 'user' },
  isAdmin: { type: Boolean, default: false },
  balance: { type: Number, default: 0 }
});

module.exports = mongoose.model('User', userSchema);
