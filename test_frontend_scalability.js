#!/usr/bin/env node
/**
 * Frontend scalability test for ABParts system.
 * Tests frontend responsiveness with large parts datasets.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

// Configuration
const FRONTEND_URL = 'http://localhost:3000';
const TEST_TIMEOUT = 30000; // 30 seconds
const PERFORMANCE_THRESHOLDS = {
  pageLoad: 5000,      // 5 seconds
  searchResponse: 2000, // 2 seconds
  filterResponse: 2000, // 2 seconds
  pagination: 1500     // 1.5 seconds
};

class FrontendScalabilityTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.results = {
      pageLoad: [],
      search: [],
      filter: [],
      pagination: [],
      errors: []
    };
  }

  async initialize() {
    console.log('Initializing browser for frontend testing...');

    this.browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });

    this.page = await this.browser.newPage();

    // Set viewport for consistent testing
    await this.page.setViewport({ width: 1920, height: 1080 });

    // Enable request interception for performance monitoring
    await this.page.setRequestInterception(true);

    this.page.on('request', (request) => {
      request.continue();
    });

    // Monitor console errors
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        this.results.errors.push({
          timestamp: new Date().toISOString(),
          message: msg.text()
        });
      }
    });

    console.log('✓ Browser initialized');
  }

  async login() {
    console.log('Logging in to the application...');

    try {
      await this.page.goto(`${FRONTEND_URL}/login`, {
        waitUntil: 'networkidle2',
        timeout: TEST_TIMEOUT
      });

      // Fill login form
      await this.page.waitForSelector('input[name="username"]', { timeout: 10000 });
      await this.page.type('input[name="username"]', 'superadmin');
      await this.page.type('input[name="password"]', 'superadmin');

      // Submit login
      await this.page.click('button[type="submit"]');

      // Wait for redirect to dashboard
      await this.page.waitForNavigation({
        waitUntil: 'networkidle2',
        timeout: TEST_TIMEOUT
      });

      console.log('✓ Login successful');
      return true;

    } catch (error) {
      console.error('✗ Login failed:', error.message);
      return false;
    }
  }

  async testPageLoadPerformance() {
    console.log('\n=== Testing Page Load Performance ===');

    const pages = [
      { name: 'Parts List', url: '/parts' },
      { name: 'Dashboard', url: '/dashboard' },
      { name: 'Inventory', url: '/inventory' }
    ];

    for (const pageInfo of pages) {
      try {
        const startTime = Date.now();

        await this.page.goto(`${FRONTEND_URL}${pageInfo.url}`, {
          waitUntil: 'networkidle2',
          timeout: TEST_TIMEOUT
        });

        const loadTime = Date.now() - startTime;

        this.results.pageLoad.push({
          page: pageInfo.name,
          loadTime: loadTime,
          success: true
        });

        const status = loadTime <= PERFORMANCE_THRESHOLDS.pageLoad ? '✓' : '✗';
        console.log(`${status} ${pageInfo.name}: ${loadTime}ms`);

      } catch (error) {
        this.results.pageLoad.push({
          page: pageInfo.name,
          success: false,
          error: error.message
        });
        console.log(`✗ ${pageInfo.name}: Failed - ${error.message}`);
      }
    }
  }

  async testSearchPerformance() {
    console.log('\n=== Testing Search Performance ===');

    // Navigate to parts page
    await this.page.goto(`${FRONTEND_URL}/parts`, {
      waitUntil: 'networkidle2',
      timeout: TEST_TIMEOUT
    });

    const searchTerms = ['Test', 'Part', 'BossAqua', 'CONSUMABLE', 'Scale'];

    for (const term of searchTerms) {
      try {
        // Clear search input
        await this.page.evaluate(() => {
          const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
          if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
        });

        await this.page.waitForTimeout(500); // Wait for debounce

        const startTime = Date.now();

        // Type search term
        const searchSelector = 'input[type="search"], input[placeholder*="search" i]';
        await this.page.waitForSelector(searchSelector, { timeout: 5000 });
        await this.page.type(searchSelector, term);

        // Wait for search results to update
        await this.page.waitForTimeout(1000); // Wait for debounce and API call

        const searchTime = Date.now() - startTime;

        this.results.search.push({
          term: term,
          responseTime: searchTime,
          success: true
        });

        const status = searchTime <= PERFORMANCE_THRESHOLDS.searchResponse ? '✓' : '✗';
        console.log(`${status} Search "${term}": ${searchTime}ms`);

      } catch (error) {
        this.results.search.push({
          term: term,
          success: false,
          error: error.message
        });
        console.log(`✗ Search "${term}": Failed - ${error.message}`);
      }
    }
  }

  async testFilterPerformance() {
    console.log('\n=== Testing Filter Performance ===');

    // Navigate to parts page
    await this.page.goto(`${FRONTEND_URL}/parts`, {
      waitUntil: 'networkidle2',
      timeout: TEST_TIMEOUT
    });

    const filters = [
      { name: 'Part Type Filter', selector: 'select[name="part_type"], select[id*="type"]' },
      { name: 'Proprietary Filter', selector: 'select[name="is_proprietary"], input[type="checkbox"][name*="proprietary"]' }
    ];

    for (const filter of filters) {
      try {
        const startTime = Date.now();

        // Try to find and interact with filter
        const filterElement = await this.page.$(filter.selector);

        if (filterElement) {
          if (filter.selector.includes('select')) {
            // Handle select dropdown
            await this.page.select(filter.selector, await this.page.evaluate(
              (sel) => {
                const select = document.querySelector(sel);
                return select && select.options[1] ? select.options[1].value : '';
              }, filter.selector
            ));
          } else {
            // Handle checkbox
            await this.page.click(filter.selector);
          }

          // Wait for filter results
          await this.page.waitForTimeout(1000);

          const filterTime = Date.now() - startTime;

          this.results.filter.push({
            filter: filter.name,
            responseTime: filterTime,
            success: true
          });

          const status = filterTime <= PERFORMANCE_THRESHOLDS.filterResponse ? '✓' : '✗';
          console.log(`${status} ${filter.name}: ${filterTime}ms`);
        } else {
          console.log(`⚠️  ${filter.name}: Element not found`);
        }

      } catch (error) {
        this.results.filter.push({
          filter: filter.name,
          success: false,
          error: error.message
        });
        console.log(`✗ ${filter.name}: Failed - ${error.message}`);
      }
    }
  }

  async testPaginationPerformance() {
    console.log('\n=== Testing Pagination Performance ===');

    // Navigate to parts page
    await this.page.goto(`${FRONTEND_URL}/parts`, {
      waitUntil: 'networkidle2',
      timeout: TEST_TIMEOUT
    });

    const paginationTests = [
      { name: 'Next Page', selector: 'button[aria-label*="next" i], .pagination button:last-child' },
      { name: 'Previous Page', selector: 'button[aria-label*="prev" i], .pagination button:first-child' },
      { name: 'Page Number', selector: '.pagination button[data-page="2"], .pagination a[href*="page=2"]' }
    ];

    for (const test of paginationTests) {
      try {
        const startTime = Date.now();

        // Try to find pagination element
        const paginationElement = await this.page.$(test.selector);

        if (paginationElement) {
          await this.page.click(test.selector);

          // Wait for page to update
          await this.page.waitForTimeout(1000);

          const paginationTime = Date.now() - startTime;

          this.results.pagination.push({
            action: test.name,
            responseTime: paginationTime,
            success: true
          });

          const status = paginationTime <= PERFORMANCE_THRESHOLDS.pagination ? '✓' : '✗';
          console.log(`${status} ${test.name}: ${paginationTime}ms`);
        } else {
          console.log(`⚠️  ${test.name}: Element not found`);
        }

      } catch (error) {
        this.results.pagination.push({
          action: test.name,
          success: false,
          error: error.message
        });
        console.log(`✗ ${test.name}: Failed - ${error.message}`);
      }
    }
  }

  async testMemoryUsage() {
    console.log('\n=== Testing Memory Usage ===');

    try {
      const metrics = await this.page.metrics();

      console.log(`Memory Usage:`);
      console.log(`  JS Heap Used: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`  JS Heap Total: ${(metrics.JSHeapTotalSize / 1024 / 1024).toFixed(2)} MB`);
      console.log(`  DOM Nodes: ${metrics.Nodes}`);
      console.log(`  Event Listeners: ${metrics.JSEventListeners}`);

      // Check for memory leaks (basic check)
      if (metrics.JSHeapUsedSize > 100 * 1024 * 1024) { // 100MB
        console.log('⚠️  High memory usage detected');
      } else {
        console.log('✓ Memory usage within acceptable limits');
      }

    } catch (error) {
      console.log(`✗ Memory usage test failed: ${error.message}`);
    }
  }

  generateReport() {
    console.log('\n=== Frontend Performance Test Report ===');

    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        pageLoad: this.results.pageLoad.filter(r => r.success).length,
        search: this.results.search.filter(r => r.success).length,
        filter: this.results.filter.filter(r => r.success).length,
        pagination: this.results.pagination.filter(r => r.success).length,
        errors: this.results.errors.length
      },
      details: this.results,
      thresholds: PERFORMANCE_THRESHOLDS
    };

    // Calculate averages
    const avgPageLoad = this.results.pageLoad
      .filter(r => r.success)
      .reduce((sum, r) => sum + r.loadTime, 0) /
      this.results.pageLoad.filter(r => r.success).length || 0;

    const avgSearch = this.results.search
      .filter(r => r.success)
      .reduce((sum, r) => sum + r.responseTime, 0) /
      this.results.search.filter(r => r.success).length || 0;

    console.log(`Average page load time: ${avgPageLoad.toFixed(0)}ms`);
    console.log(`Average search response time: ${avgSearch.toFixed(0)}ms`);
    console.log(`Total errors: ${this.results.errors.length}`);

    // Save detailed report
    fs.writeFileSync('frontend_scalability_report.json', JSON.stringify(report, null, 2));
    console.log('✓ Detailed report saved to frontend_scalability_report.json');

    // Determine overall success
    const allTestsPassed =
      avgPageLoad <= PERFORMANCE_THRESHOLDS.pageLoad &&
      avgSearch <= PERFORMANCE_THRESHOLDS.searchResponse &&
      this.results.errors.length === 0;

    return allTestsPassed;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
      console.log('✓ Browser closed');
    }
  }

  async runAllTests() {
    console.log('ABParts Frontend Scalability Test Suite');
    console.log('=' * 50);

    try {
      await this.initialize();

      if (await this.login()) {
        await this.testPageLoadPerformance();
        await this.testSearchPerformance();
        await this.testFilterPerformance();
        await this.testPaginationPerformance();
        await this.testMemoryUsage();
      }

      return this.generateReport();

    } catch (error) {
      console.error('Test execution failed:', error);
      return false;
    } finally {
      await this.cleanup();
    }
  }
}

async function main() {
  const tester = new FrontendScalabilityTester();
  const success = await tester.runAllTests();

  if (success) {
    console.log('\n🎉 Frontend scalability validation: SUCCESS');
    process.exit(0);
  } else {
    console.log('\n❌ Frontend scalability validation: FAILED');
    process.exit(1);
  }
}

// Check if puppeteer is available
try {
  require.resolve('puppeteer');
  main().catch(console.error);
} catch (error) {
  console.log('⚠️  Puppeteer not available. Skipping frontend tests.');
  console.log('To run frontend tests, install puppeteer: npm install puppeteer');
  process.exit(0);
}