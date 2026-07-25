# Tour Localization Debug Guide

## Current Status
- ✅ **Close button (X) fixed** - Now properly closes tour
- ⚠️ **Next button still showing English** - Despite comprehensive fixes

## Enhanced Implementation

### Latest Changes Made:
1. **Forced Tour Restart on Language Change** - Tour automatically restarts when language changes
2. **Enhanced Debug Logging** - More detailed console output to track translation loading
3. **Timestamp-based Keys** - Ensures complete component re-mounting
4. **Translation Verification** - Explicit checks for Greek translations

### Debug Steps

#### 1. **Browser Console Testing**
```javascript
// Copy and paste this into browser console:
// (Also available in test_tour_translations.js file)

console.log('=== Tour Translation Test ===');

// Check stored language
const storedLang = localStorage.getItem('localizationPreferences');
console.log('Stored language:', JSON.parse(storedLang || '{}'));

// Test Greek translations
fetch('/locales/el.json')
  .then(response => response.json())
  .then(data => {
    console.log('Greek translations:');
    console.log('  next:', data.tour?.next, '(should be "Επόμενο")');
    console.log('  step:', data.tour?.step, '(should be "Βήμα")');
    console.log('  of:', data.tour?.of, '(should be "από")');
  });

// Trigger language change
window.dispatchEvent(new CustomEvent('languageChanged', { 
  detail: { language: 'el' } 
}));
```

#### 2. **Console Logs to Look For**
When testing, you should see these logs:
```
🎯 Joyride locale object created: {next: "Επόμενο", step: "Βήμα", of: "από", ...}
🌍 Current language from hook: el
🔄 Force update counter: 1
🔤 Raw translation values: {nextText: "Επόμενο", stepText: "Βήμα", ofText: "από"}
🇬🇷 Greek check - next should be "Επόμενο": true
🇬🇷 Greek check - step should be "Βήμα": true
🇬🇷 Greek check - of should be "από": true
🔄 Forcing Joyride restart due to language change
Language change event detected, forcing tour re-render
```

#### 3. **Step-by-Step Testing Process**
1. **Open Application**: http://localhost:3000
2. **Open Browser Console**: F12 → Console tab
3. **Switch to Greek**: Use language selector (Ελληνικά)
4. **Check Console**: Look for 🇬🇷 Greek check logs
5. **Start Tour**: Click help (?) button → Start any tour
6. **Verify Buttons**: Should show "Επόμενο (Βήμα X από Y)"

#### 4. **If Still Showing English**

**Immediate Actions:**
```bash
# Hard refresh browser
Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)

# Clear browser cache completely
# Or open incognito/private mode

# Check frontend logs
docker-compose logs web

# Restart frontend container
docker-compose restart web
```

**Advanced Debugging:**
```javascript
// In browser console, check if Joyride is receiving correct locale
const joyrideElement = document.querySelector('.react-joyride__tooltip');
if (joyrideElement) {
  console.log('Joyride element found');
  const buttons = joyrideElement.querySelectorAll('button');
  buttons.forEach((btn, i) => {
    console.log(`Button ${i}: "${btn.textContent}"`);
  });
}
```

## Possible Root Causes

### 1. **React Joyride Internal Caching**
- Joyride might be caching the locale internally
- **Solution**: The enhanced version now forces complete restart

### 2. **Translation Loading Timing**
- Translations might not be loaded when Joyride initializes
- **Solution**: Added explicit translation verification

### 3. **Component Re-rendering Issues**
- React might not be detecting locale changes
- **Solution**: Added timestamp-based keys and force updates

### 4. **Browser Caching**
- Old JavaScript might be cached
- **Solution**: Hard refresh or incognito mode

## Alternative Approaches (If Still Not Working)

### Option 1: Custom Button Rendering
If React Joyride continues to ignore locale, we can override button rendering:

```javascript
// Add to GuidedTour component
const customButtons = {
  primary: ({ ...props }) => (
    <button {...props} style={joyrideStyles.buttonNext}>
      {t('tour.next')}
    </button>
  )
};

// Add to Joyride props
floaterProps={{
  ...floaterProps,
  options: {
    ...floaterProps.options,
    primaryButton: customButtons.primary
  }
}}
```

### Option 2: Force Locale via DOM Manipulation
```javascript
// After Joyride renders, manually update button text
useEffect(() => {
  if (tourState.run) {
    setTimeout(() => {
      const nextButton = document.querySelector('.react-joyride__tooltip button[data-action="next"]');
      if (nextButton && currentLanguage === 'el') {
        nextButton.textContent = 'Επόμενο';
      }
    }, 100);
  }
}, [tourState.run, tourState.stepIndex, currentLanguage]);
```

## Files Modified in Latest Fix

1. **`frontend/src/components/GuidedTour.js`**
   - Added forced tour restart on language change
   - Enhanced debug logging with Greek verification
   - Added timestamp to component keys
   - Added ref for programmatic control

2. **`test_tour_translations.js`**
   - Browser console test script
   - Verifies translation loading
   - Tests manual language change events

## Success Criteria

- ✅ Close button works properly
- ⚠️ Next button shows "Επόμενο" in Greek
- ⚠️ Step counter shows "Βήμα X από Y" in Greek
- ✅ Console logs show correct translations loaded
- ✅ Language switching triggers tour restart

## Next Steps

1. **Test the enhanced version** with the new debug logging
2. **Check console logs** to verify translations are loading correctly
3. **If still English**, try the alternative approaches above
4. **Report findings** - the console logs will help identify the exact issue

The enhanced implementation should now provide much clearer debugging information to identify why React Joyride isn't applying the locale correctly.