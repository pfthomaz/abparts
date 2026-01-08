// Test script to verify text-to-speech functionality
// Run this in the browser console when the ChatWidget is open

console.log('Testing AutoBoss AI Assistant Voice Functionality');

// Test 1: Check if Web Speech API is available
console.log('1. Web Speech API Support:');
console.log('  - SpeechRecognition:', !!(window.SpeechRecognition || window.webkitSpeechRecognition));
console.log('  - SpeechSynthesis:', !!window.speechSynthesis);

// Test 2: Check available voices
if (window.speechSynthesis) {
  const voices = window.speechSynthesis.getVoices();
  console.log('2. Available Voices:', voices.length);
  
  // Show voices for each language
  const languageVoices = {
    'en': voices.filter(v => v.lang.startsWith('en')),
    'el': voices.filter(v => v.lang.startsWith('el')),
    'ar': voices.filter(v => v.lang.startsWith('ar')),
    'es': voices.filter(v => v.lang.startsWith('es')),
    'tr': voices.filter(v => v.lang.startsWith('tr')),
    'no': voices.filter(v => v.lang.startsWith('no') || v.lang.startsWith('nb'))
  };
  
  Object.entries(languageVoices).forEach(([lang, langVoices]) => {
    console.log(`  - ${lang.toUpperCase()}: ${langVoices.length} voices`);
    if (langVoices.length > 0) {
      console.log(`    Best voice: ${langVoices[0].name} (${langVoices[0].lang})`);
    }
  });
}

// Test 3: Test text-to-speech with sample text
console.log('3. Testing Text-to-Speech:');
const testTexts = {
  'en': 'Hello! I am your AutoBoss AI Assistant. How can I help you today?',
  'el': 'Γεια σας! Είμαι ο βοηθός AI του AutoBoss. Πώς μπορώ να σας βοηθήσω σήμερα;',
  'ar': 'مرحبا! أنا مساعد الذكي AutoBoss. كيف يمكنني مساعدتك اليوم؟',
  'es': '¡Hola! Soy tu asistente de IA AutoBoss. ¿Cómo puedo ayudarte hoy?',
  'tr': 'Merhaba! AutoBoss AI Asistanınızım. Bugün size nasıl yardımcı olabilirim?',
  'no': 'Hei! Jeg er din AutoBoss AI-assistent. Hvordan kan jeg hjelpe deg i dag?'
};

function testSpeech(language) {
  if (!window.speechSynthesis) {
    console.log(`  - ${language.toUpperCase()}: Speech synthesis not supported`);
    return;
  }
  
  const utterance = new SpeechSynthesisUtterance(testTexts[language]);
  const voices = window.speechSynthesis.getVoices();
  const voice = voices.find(v => v.lang.startsWith(language)) || voices[0];
  
  if (voice) {
    utterance.voice = voice;
    utterance.lang = voice.lang;
  }
  
  utterance.rate = 0.9;
  utterance.pitch = 1;
  utterance.volume = 0.8;
  
  utterance.onstart = () => console.log(`  - ${language.toUpperCase()}: ✓ Speech started`);
  utterance.onend = () => console.log(`  - ${language.toUpperCase()}: ✓ Speech completed`);
  utterance.onerror = (e) => console.log(`  - ${language.toUpperCase()}: ✗ Error: ${e.error}`);
  
  window.speechSynthesis.speak(utterance);
}

// Test each language (uncomment to test)
// testSpeech('en');

console.log('4. Manual Testing Instructions:');
console.log('  - Open the AI Assistant chat widget');
console.log('  - Click the speaker icon in the header to enable auto-speak');
console.log('  - Send a message and verify the response is spoken aloud');
console.log('  - Click individual speak buttons on messages');
console.log('  - Use voice commands: "repeat", "stop", "clear", "help"');
console.log('  - Test in different languages by changing the language selector');

console.log('5. To test a specific language, run: testSpeech("en") // or el, ar, es, tr, no');