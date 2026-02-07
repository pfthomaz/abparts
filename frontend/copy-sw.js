const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'public', 'service-worker.js');
const dest = path.join(__dirname, 'build', 'service-worker.js');

if (fs.existsSync(source)) {
  fs.copyFileSync(source, dest);
  console.log('✓ Service worker copied to build folder');
} else {
  console.warn('⚠ Service worker source file not found at:', source);
}
