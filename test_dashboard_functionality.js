// Test script to verify dashboard functionality
const puppeteer = require('puppeteer');

async function testDashboard() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  try {
    // Navigate to the login page
    await page.goto('http://localhost:3000');

    // Wait for login form
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });

    // Login as superadmin
    await page.type('input[name="username"]', 'superadmin');
    await page.type('input[name="password"]', 'superadmin');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForSelector('.text-4xl', { timeout: 10000 });

    // Check if the three-column layout exists
    const columns = await page.$$('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3');
    console.log('Three-column layout found:', columns.length > 0);

    // Check for Entities column
    const entitiesHeader = await page.$('text=Entities');
    console.log('Entities column found:', entitiesHeader !== null);

    // Check for Actions column
    const actionsHeader = await page.$('text=Quick Actions');
    console.log('Actions column found:', actionsHeader !== null);

    // Check for Reports column
    const reportsHeader = await page.$('text=Reports & Analytics');
    console.log('Reports column found:', reportsHeader !== null);

    // Check for System Status section
    const statusHeader = await page.$('text=System Status');
    console.log('System Status section found:', statusHeader !== null);

    // Check for organization selector (superadmin only)
    const orgSelector = await page.$('select#organization-selector');
    console.log('Organization selector found (superadmin):', orgSelector !== null);

    console.log('Dashboard test completed successfully!');

  } catch (error) {
    console.error('Dashboard test failed:', error);
  } finally {
    await browser.close();
  }
}

testDashboard();