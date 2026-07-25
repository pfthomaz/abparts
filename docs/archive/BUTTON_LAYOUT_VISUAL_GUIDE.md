# Button Layout Visual Guide

## Final Button Positioning

### Desktop/Mobile Layout

```
┌─────────────────────────────────────────┐
│                                         │
│         Main Content Area               │
│                                         │
│                                         │
│                                         │
│                                         │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│                                         │
│                                    ┌────┤ 208px (13rem)
│                                    │ 🌊 │ Action Menu
│                                    │ 🔧 │ (when FAB open)
│                                    │ 📦 │
│                                    └────┤
│                                         │
│  ┌────┐                          ┌────┐│ 144px (9rem)
│  │ 💬 │                          │ + │││ FAB
│  └────┘                          └────┘│
│                                         │
│                                  ┌────┐ │ 80px (5rem)
│                                  │ ? │ │ Tour Button
│                                  └────┘ │
└─────────────────────────────────────────┘
  ↑                                      ↑
  16px (left-4)                   16px (right-4)
```

## Button Details

### Chat Button (AI Assistant)
- **Position**: Bottom-left
- **Distance from left**: 16px (`left-4`)
- **Distance from bottom**: 80px (`5rem`)
- **Color**: Blue (`bg-blue-600`)
- **Icon**: 💬 (chat bubble)
- **Purpose**: Open AI Assistant chat

### Tour Button (Help)
- **Position**: Bottom-right
- **Distance from right**: 16px (`right-4`)
- **Distance from bottom**: 80px (`5rem`)
- **Color**: Blue (`bg-blue-600`)
- **Icon**: ? (question mark)
- **Purpose**: Open guided tours menu

### FAB (Quick Actions)
- **Position**: Bottom-right (above Tour)
- **Distance from right**: 16px (`right-4`)
- **Distance from bottom**: 144px (`9rem`)
- **Color**: Gradient blue-purple
- **Icon**: + (plus sign)
- **Purpose**: Quick access to primary actions

### Action Menu (when FAB is open)
- **Position**: Bottom-right (above FAB)
- **Distance from right**: 16px (`right-4`)
- **Distance from bottom**: 208px (`13rem`)
- **Contains**: 3 action buttons with labels
  - 🌊 Wash Nets
  - 🔧 Daily Service
  - 📦 Order Parts

## Spacing Between Buttons

| From | To | Distance |
|------|-----|----------|
| Tour | FAB | 64px (4rem) |
| FAB | Action Menu | 64px (4rem) |
| Chat | Tour | Full width minus 32px |

## Mobile Safe Areas

All buttons use `env(safe-area-inset-bottom)` to respect:
- iPhone notches
- Android gesture bars
- Home indicators

**Formula**: `max(Xrem, calc(Y + env(safe-area-inset-bottom)))`

This ensures buttons are always above the safe area on all devices.

## Interaction States

### FAB States

**Closed** (default):
- Shows: `+` icon
- Color: Blue-purple gradient
- Hover: Scales to 110%

**Open** (clicked):
- Shows: `✕` icon (rotated 45°)
- Color: Red
- Action menu appears above
- Backdrop appears (semi-transparent black)

### Action Menu Animation

Each action button animates in with:
- Fade in effect
- Slide up effect
- Staggered delay (50ms between each)

## Z-Index Layers

| Element | Z-Index | Purpose |
|---------|---------|---------|
| Backdrop | 40 | Dim background when FAB open |
| Chat Button | 40 | Always accessible |
| Tour Button | 50 | Always accessible |
| FAB | 50 | Primary quick action |
| Action Menu | 50 | Same layer as FAB |

## Responsive Behavior

### Mobile (< 768px)
- All buttons: 16px from edges (`left-4`, `right-4`)
- FAB size: 64px × 64px
- Action buttons: 56px × 56px

### Desktop (≥ 768px)
- All buttons: 32px from edges (`md:left-8`, `md:right-8`)
- FAB size: 64px × 64px (same)
- Action buttons: 56px × 56px (same)

## Accessibility

All buttons include:
- `aria-label` for screen readers
- `aria-expanded` for FAB (true/false)
- Focus rings on keyboard navigation
- Sufficient touch target size (minimum 44px)

## Color Coding

| Button | Color | Meaning |
|--------|-------|---------|
| Chat | Blue | Information/Help |
| Tour | Blue | Information/Help |
| FAB (closed) | Blue-Purple | Primary Action |
| FAB (open) | Red | Close/Cancel |
| Wash Nets | Teal | Water-related |
| Daily Service | Orange | Maintenance |
| Order Parts | Blue | Inventory |

## Testing Checklist

- [ ] Chat button visible bottom-left
- [ ] Tour button visible bottom-right
- [ ] FAB visible above Tour button
- [ ] No overlap between any buttons
- [ ] FAB opens to show 3 actions
- [ ] Action menu appears above FAB
- [ ] Labels are readable
- [ ] All buttons clickable
- [ ] Works on mobile (< 768px)
- [ ] Works on desktop (≥ 768px)
- [ ] Works on iPhone with notch
- [ ] Works on Android with gesture bar

---

**Last Updated**: January 30, 2026  
**Status**: Final positioning implemented ✅
