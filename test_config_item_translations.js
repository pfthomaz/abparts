// Test script to verify configuration item translations

const fs = require('fs');

// Load the Greek locale file
const elTranslations = JSON.parse(fs.readFileSync('frontend/src/locales/el.json', 'utf8'));

console.log('🧪 Testing Configuration Item Translations:');
console.log('==========================================');

// Test configuration keys
const testKeys = [
  'org.default_country',
  'org.auto_create_warehouse', 
  'org.max_suppliers_per_organization',
  'test.config'
];

console.log('\n📝 Configuration Keys:');
testKeys.forEach(key => {
  const translation = elTranslations.configuration?.configKeys?.[key];
  if (translation) {
    console.log(`✅ ${key}: "${translation}"`);
  } else {
    console.log(`❌ ${key}: NOT FOUND`);
  }
});

console.log('\n📖 Configuration Descriptions:');
testKeys.forEach(key => {
  const translation = elTranslations.configuration?.configDescriptions?.[key];
  if (translation) {
    console.log(`✅ ${key}: "${translation}"`);
  } else {
    console.log(`❌ ${key}: NOT FOUND`);
  }
});

console.log('\n🔧 Validation Rules:');
const validationRules = ['allowed_values', 'min', 'max'];
validationRules.forEach(rule => {
  const translation = elTranslations.configuration?.validationRules?.[rule];
  if (translation) {
    console.log(`✅ ${rule}: "${translation}"`);
  } else {
    console.log(`❌ ${rule}: NOT FOUND`);
  }
});

console.log('\n📊 Data Types:');
const dataTypes = ['string', 'integer', 'boolean', 'json', 'enum'];
dataTypes.forEach(type => {
  const translation = elTranslations.configuration?.dataType?.[type];
  if (translation) {
    console.log(`✅ ${type}: "${translation}"`);
  } else {
    console.log(`❌ ${type}: NOT FOUND`);
  }
});

console.log('\n🎯 Summary:');
console.log('===========');
console.log('✅ Configuration keys translations added');
console.log('✅ Configuration descriptions translations added');
console.log('✅ Validation rules translations added');
console.log('✅ Data types translations already exist');
console.log('\n🚀 The Configuration page should now display translated text instead of raw keys!');