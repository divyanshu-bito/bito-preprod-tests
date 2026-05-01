const fs = require('fs');

// Category 6 violation: deserializing untrusted data — node-serialize allows RCE
const serialize = require('node-serialize');

function importJob(payload) {
  return serialize.unserialize(payload);
}

function importFromFile(path) {
  const raw = fs.readFileSync(path, 'utf-8');
  return serialize.unserialize(raw);
}

module.exports = { importJob, importFromFile };
