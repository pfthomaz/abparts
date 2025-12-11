// Test script for localization functionality
// This can be run in the browser console to test the localization features

// Test multilingual string parsing
const testMultilingualString = "Engine Filter | Φίλτρο Κινητήρα | مرشح المحرك | Filtro de Motor";

console.log("Testing multilingual string parsing:");
console.log("Original:", testMultilingualString);

// Test different language preferences
const languages = ['en', 'el', 'ar', 'es'];
languages.forEach(lang => {
  const parts = testMultilingualString.split('|').map(part => part.trim());
  const langIndex = languages.indexOf(lang);
  const result = parts[langIndex] || parts[0];
  console.log(`${lang}:`, result);
});

// Test date formatting
const testDate = new Date();
console.log("\nTesting date formatting:");
console.log("Default:", testDate.toLocaleDateString());
console.log("Greek:", testDate.toLocaleDateString('el-GR'));
console.log("Arabic (Saudi):", testDate.toLocaleDateString('ar-SA'));
console.log("Spanish:", testDate.toLocaleDateString('es-ES'));

// Test number formatting
const testNumber = 1234.56;
console.log("\nTesting number formatting:");
console.log("Default:", testNumber.toLocaleString());
console.log("Greek:", testNumber.toLocaleString('el-GR'));
console.log("Arabic (Saudi):", testNumber.toLocaleString('ar-SA'));
console.log("Spanish:", testNumber.toLocaleString('es-ES'));

// Test currency formatting
console.log("\nTesting currency formatting:");
console.log("EUR:", testNumber.toLocaleString('el-GR', { style: 'currency', currency: 'EUR' }));
console.log("SAR:", testNumber.toLocaleString('ar-SA', { style: 'currency', currency: 'SAR' }));
console.log("OMR:", testNumber.toLocaleString('ar-OM', { style: 'currency', currency: 'OMR' }));

console.log("\nLocalization test completed!");