// Category 5 violation: secrets hardcoded in source instead of env vars
module.exports = {
  AWS_ACCESS_KEY_ID: 'AKIAIOSFODNN7EXAMPLE',
  AWS_SECRET_ACCESS_KEY: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  STRIPE_SECRET_KEY: 'sk_live_51HxxxxxxxxxxxxxxxxxxxxxxxxxxxxA',
  JWT_SECRET: 'super-secret-jwt-signing-key-prod-2025',
  DB_PASSWORD: 'admin123',
  DEBUG: true,
  NODE_ENV: 'production'
};
