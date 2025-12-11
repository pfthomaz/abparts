# Install date-fns for Calendar View

## Installation

Run this command in the frontend directory:

```bash
cd frontend
npm install date-fns
```

## What is date-fns?

date-fns is a modern JavaScript date utility library that provides comprehensive functions for manipulating dates.

We're using it for:
- Calculating date ranges (15 days before/after)
- Formatting dates for display
- Calculating differences between dates
- Generating day intervals for the calendar grid

## Size

- **Minimal bundle size**: ~13KB (tree-shakeable)
- Only imports the functions we use
- Much lighter than moment.js

## Functions Used

- `subDays` - Subtract days from a date
- `addDays` - Add days to a date  
- `differenceInDays` - Calculate days between two dates
- `eachDayOfInterval` - Generate array of days in a range
- `format` - Format dates for display
- `isToday` - Check if a date is today
- `parseISO` - Parse ISO date strings

## After Installation

1. Restart the development server:
   ```bash
   npm start
   ```

2. The Calendar View tab should now work without errors!

## Alternative (if npm install fails)

If you can't install via npm, you can use the browser CDN version, but it's not recommended for production.
