// Debug script to test tour translations
// Run this in the browser console while on the tour page

console.log('=== Tour Translation Debug ===');

// Check if translation hook is available
if (window.React && window.React.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED) {
  console.log('React is available');
} else {
  console.log('React not found in window');
}

// Check current language
const currentLang = localStorage.getItem('preferredLanguage') || 'en';
console.log('Current language:', currentLang);

// Try to access translation function
try {
  // This is a hack to access the translation context
  const tourButton = document.querySelector('[title*="help"], [title*="βοήθεια"], [title*="مساعدة"]');
  if (tourButton) {
    console.log('Tour button found:', tourButton);
  }
  
  // Check if locale files are loaded
  fetch('/locales/el.json')
    .then(response => response.json())
    .then(data => {
      console.log('Greek locale loaded:', !!data);
      console.log('Tour section exists:', !!data.tour);
      if (data.tour) {
        console.log('Tour.next:', data.tour.next);
        console.log('Tour.step:', data.tour.step);
        console.log('Tour.of:', data.tour.of);
      }
    })
    .catch(err => console.log('Failed to load Greek locale:', err));
    
} catch (error) {
  console.log('Error accessing translation system:', error);
}

// Check if Joyride is loaded
if (window.Joyride) {
  console.log('Joyride is available globally');
} else {
  console.log('Joyride not found in window');
}

console.log('=== End Debug ===');