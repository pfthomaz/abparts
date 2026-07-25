# Voice Debug Instructions

## Quick Console Debug

Copy and paste this into your browser console to debug speech synthesis:

```javascript
// === INLINE SPEECH SYNTHESIS DEBUG ===
console.log('🎤 AutoBoss AI Assistant - Speech Debug');

// Check Web Speech API support
console.log('1. Web Speech API Support:');
console.log('  - speechSynthesis:', !!window.speechSynthesis);
console.log('  - SpeechSynthesisUtterance:', !!window.SpeechSynthesisUtterance);

if (!window.speechSynthesis) {
  console.error('❌ Speech Synthesis not supported');
} else {
  // Check current state
  console.log('2. Current State:');
  console.log('  - speaking:', window.speechSynthesis.speaking);
  console.log('  - pending:', window.speechSynthesis.pending);
  console.log('  - paused:', window.speechSynthesis.paused);

  // Test basic speech
  window.testSpeech = function(text = 'Hello, this is a test of the AutoBoss AI Assistant speech synthesis.') {
    console.log('🔊 Testing speech:', text);
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    setTimeout(() => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 0.9;
      
      utterance.onstart = () => console.log('✅ Speech started');
      utterance.onend = () => console.log('✅ Speech completed');
      utterance.onerror = (e) => console.error('❌ Speech error:', e.error);
      
      window.speechSynthesis.speak(utterance);
      
      // Monitor for issues
      setTimeout(() => {
        if (!window.speechSynthesis.speaking) {
          console.warn('⚠️ Speech did not start within 500ms');
        }
      }, 500);
    }, 100);
  };

  // Test long speech
  window.testLongSpeech = function() {
    const longText = 'This is a longer test message to check if the AutoBoss AI Assistant speech synthesis can handle extended text without cutting off prematurely. The system should speak this entire message clearly and completely without interruption.';
    window.testSpeech(longText);
  };

  // Cancel speech
  window.cancelSpeech = function() {
    window.speechSynthesis.cancel();
    console.log('🛑 Speech cancelled');
  };

  console.log('3. Test Functions Available:');
  console.log('  - testSpeech() - Test basic speech');
  console.log('  - testLongSpeech() - Test long message');
  console.log('  - cancelSpeech() - Cancel current speech');
}
```

## Step-by-Step Debugging

### 1. Basic Test
```javascript
testSpeech();
```

### 2. Long Message Test
```javascript
testLongSpeech();
```

### 3. Check Voice Button State
Look at the AI Assistant chat widget:
- 🔴 Red button = Voice disabled
- 🟢 Green button = Voice enabled

### 4. Test Auto-Speak
1. Click the voice button to turn it green
2. Send a message to the AI
3. Listen for the response to be spoken

### 5. Test Individual Speak Buttons
Click the small speaker icons on AI response messages

## Common Issues & Solutions

### Issue: Speech cuts off after 1 second
**Cause**: Browser speech synthesis bug
**Solution**: 
```javascript
// Force resume if paused
setInterval(() => {
  if (window.speechSynthesis.paused && window.speechSynthesis.speaking) {
    window.speechSynthesis.resume();
  }
}, 1000);
```

### Issue: No sound at all
**Causes**: 
- Browser permissions
- Audio blocked
- No voices available

**Check**:
```javascript
// Check voices
console.log('Available voices:', window.speechSynthesis.getVoices().length);

// Check audio permissions
navigator.permissions.query({name: 'microphone'}).then(result => {
  console.log('Microphone permission:', result.state);
});
```

### Issue: Voice button not changing color
**Check**: Look for JavaScript errors in console when clicking the button

### Issue: Auto-speak not working
**Check**: 
1. Is the button green?
2. Are there console errors?
3. Try manual speak button first

## Browser-Specific Notes

### Chrome
- May pause speech unexpectedly (our code handles this)
- Requires user interaction before audio

### Safari
- More restrictive audio policies
- May need user gesture for each speech

### Firefox
- Limited voice selection
- Generally more reliable

## If All Else Fails

Try this minimal test:
```javascript
const utterance = new SpeechSynthesisUtterance('Test');
utterance.onstart = () => console.log('Started');
utterance.onend = () => console.log('Ended');
utterance.onerror = (e) => console.log('Error:', e.error);
window.speechSynthesis.speak(utterance);
```

If this doesn't work, the issue is with your browser's speech synthesis support.