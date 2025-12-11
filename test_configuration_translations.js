// Test script to verify configuration translations are working

const fs = require('fs');

// Load the Greek locale file
const elTranslations = JSON.parse(fs.readFileSync('frontend/src/locales/el.json', 'utf8'));

// Test key paths that the Configuration page uses
const testKeys = [
  'configuration.title',
  'configuration.subtitle', 
  'configuration.tabs.organization',
  'configuration.category.organization.title',
  'configuration.tips.title',
  'configuration.modal.templates'
];

console.log('🧪 Testing Configuration Translation Keys:');
console.log('==========================================');

testKeys.forEach(key => {
  const keys = key.split('.');
  let value = elTranslations;
  
  // Navigate through nested structure
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      value = null;
      break;
    }
  }
  
  if (value && typeof value === 'string') {
    console.log(`✅ ${key}: "${value}"`);
  } else {
    console.log(`❌ ${key}: NOT FOUND`);
  }
});

console.log('\n🎯 Configuration object structure:');
console.log('==================================');
if (elTranslations.configuration) {
  console.log('✅ configuration object exists');
  console.log('Keys:', Object.keys(elTranslations.configuration));
  
  if (elTranslations.configuration.tabs) {
    console.log('✅ configuration.tabs exists');
    console.log('Tab keys:', Object.keys(elTranslations.configuration.tabs));
  }
  
  if (elTranslations.configuration.category) {
    console.log('✅ configuration.category exists');
    console.log('Category keys:', Object.keys(elTranslations.configuration.category));
  }
} else {
  console.log('❌ configuration object missing');
}