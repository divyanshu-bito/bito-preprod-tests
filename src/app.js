const express = require('express');
const app = express();
const config = require('./config');
const loginRouter = require('./auth/login');
const adminRouter = require('./admin/admin');

app.use(express.json());

// Category 5 violation: debug mode in production
app.set('env', 'development');
app.locals.debug = true;

// Category 3 violation: wide-open CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Access-Control-Allow-Methods', '*');
  res.header('Access-Control-Allow-Headers', '*');
  next();
});

app.use('/auth', loginRouter);
app.use('/admin', adminRouter);

// Category 5 violation: leaking stack traces in error responses
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    config: config
  });
});

app.listen(3000);
