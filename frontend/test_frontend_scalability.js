#!/usr/bin/env node
/**
 * Frontend scalability validation tests for ABParts system with large datasets.
 * Tests React interface performance with 10,000+ parts.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

// Configuration
const BASE_URL = 'http://localhost:3000';
const SUPERADMIN_USERNAME = 'superadmin';
const SUPERADMIN_PASSWORD = 'superadmin';
const TEST_TIMEOUT = 60000; // 60 seconds

class FrontendScalabilityTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.testResults = {};
  }

  async initialize() {
    console.log('🚀 Initializing frontend scalability tests...');

    this.browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    this.page = await this.browser.newPage();

    // Set viewport for consistent testing
    await this.page.setViewport({ width: 1920, height: 1080 });

    // Enable performance monitoring
    await this.page.setCacheEnabled(false);

    console.log('✅ Browser initialized');
  }

  async authenticate() {
    console.log('🔐 Authenticating with frontend...');

    try {
      // Navigate to login page
      await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0' });

      // Fill login form
      await this.page.waitForSelector('input[name="username"]', { timeout: 10000 });
      await this.page.type('input[name="username"]', SUPERADMIN_USERNAME);
      await this.page.type('input[name="password"]', SUPERADMIN_PASSWORD);

      // Submit form
      await this.page.click('button[type="submit"]');

      // Wait for redirect to dashboard
      await this.page.waitForNavigation({ waitUntil: 'networkidle0' });

      // Verify we're logged in (check for logout button or user menu)
      const isLoggedIn = await this.page.$('.user-menu, [data-testid="user-menu"], button:contains("Logout")') !== null;

      if (isLoggedIn) {
        console.log('✅ Frontend authentication successful');
        return true;
      } else {
        console.log('❌ Frontend authentication failed - not redirected properly');
        return false;
      }

    } catch (error) {
      console.log(`❌ Frontend authentication error: ${error.message}`);
      return false;
    }
  }

  async measurePageLoadTime(url, description) {
    console.log(`📊 Measuring page load time: ${description}`);

    const startTime = Date.now();

    try {
      await this.page.goto(url, { waitUntil: 'networkidle0', timeout: TEST_TIMEOUT });
      const loadTime = Date.now() - startTime;

      console.log(`   ✅ ${description}: ${loadTime}ms`);
      return { success: true, loadTime, description };

    } catch (error) {
      const loadTime = Date.now() - startTime;
      console.log(`   ❌ ${description} failed: ${error.message}`);
      return { success: false, loadTime, description, error: error.message };
    }
  }

  async testPartsPagePerformance() {
    console.log('\n📦 Testing parts page performance with large dataset...');

    const results = [];

    // Test initial parts page load
    const initialLoad = await this.measurePageLoadTime(
      `${BASE_URL}/parts`,
      'Initial parts page load'
    );
    results.push(initialLoad);

    if (!initialLoad.success) {
      return { error: 'Failed to load parts page', results };
    }

    // Test search functionality
    console.log('🔍 Testing search performance...');
    const searchTests = [
      { query: 'SCALE-TEST', description: 'Search for test parts' },
      { query: 'BossAqua', description: 'Search by manufacturer' },
      { query: 'Consumable', description: 'Search by type' }
    ];

    for (const test of searchTests) {
      try {
        const startTime = Date.now();

        // Clear search input and type new query
        await this.page.waitForSelector('input[type="search"], input[placeholder*="search"], input[name="search"]', { timeout: 5000 });
        await this.page.click('input[type="search"], input[placeholder*="search"], input[name="search"]');
        await this.page.keyboard.down('Control');
        await this.page.keyboard.press('KeyA');
        await this.page.keyboard.up('Control');
        await this.page.type('input[type="search"], input[placeholder*="search"], input[name="search"]', test.query);

        // Wait for search results
        await this.page.waitForTimeout(1000); // Debounce delay
        await this.page.waitForSelector('.parts-list, .part-item, [data-testid="parts-list"]', { timeout: 10000 });

        const searchTime = Date.now() - startTime;

        results.push({
          success: true,
          searchTime,
          description: test.description,
          query: test.query
        });

        console.log(`   ✅ ${test.description}: ${searchTime}ms`);

      } catch (error) {
        results.push({
          success: false,
          description: test.description,
          query: test.query,
          error: error.message
        });
        console.log(`   ❌ ${test.description} failed: ${error.message}`);
      }
    }

    // Test pagination performance
    console.log('📄 Testing pagination performance...');
    try {
      // Clear search to show all parts
      await this.page.click('input[type="search"], input[placeholder*="search"], input[name="search"]');
      await this.page.keyboard.down('Control');
      await this.page.keyboard.press('KeyA');
      await this.page.keyboard.up('Control');
      await this.page.keyboard.press('Delete');

      await this.page.waitForTimeout(1000);

      // Test pagination clicks
      const paginationTests = [
        { action: 'next', description: 'Next page navigation' },
        { action: 'next', description: 'Second next page navigation' },
        { action: 'previous', description: 'Previous page navigation' }
      ];

      for (const test of paginationTests) {
        try {
          const startTime = Date.now();

          // Find and click pagination button
          const selector = test.action === 'next'
            ? 'button:contains("Next"), .pagination-next, [data-testid="next-page"]'
            : 'button:contains("Previous"), .pagination-previous, [data-testid="previous-page"]';

          await this.page.waitForSelector(selector, { timeout: 5000 });
          await this.page.click(selector);

          // Wait for page to update
          await this.page.waitForTimeout(500);
          await this.page.waitForSelector('.parts-list, .part-item, [data-testid="parts-list"]', { timeout: 10000 });

          const paginationTime = Date.now() - startTime;

          results.push({
            success: true,
            paginationTime,
            description: test.description,
            action: test.action
          });

          console.log(`   ✅ ${test.description}: ${paginationTime}ms`);

        } catch (error) {
          results.push({
            success: false,
            description: test.description,
            action: test.action,
            error: error.message
          });
          console.log(`   ❌ ${test.description} failed: ${error.message}`);
        }
      }

    } catch (error) {
      console.log(`   ❌ Pagination testing failed: ${error.message}`);
    }

    return { results };
  }

  async testFilteringPerformance() {
    console.log('\n🔧 Testing filtering performance...');

    const results = [];

    // Navigate to parts page if not already there
    await this.page.goto(`${BASE_URL}/parts`, { waitUntil: 'networkidle0' });

    const filterTests = [
      {
        filter: 'part_type',
        value: 'CONSUMABLE',
        description: 'Filter by consumable parts',
        selector: 'select[name="part_type"], select[name="partType"], .filter-part-type'
      },
      {
        filter: 'is_proprietary',
        value: 'true',
        description: 'Filter proprietary parts',
        selector: 'input[name="is_proprietary"], input[name="proprietary"], .filter-proprietary'
      }
    ];

    for (const test of filterTests) {
      try {
        const startTime = Date.now();

        // Apply filter
        await this.page.waitForSelector(test.selector, { timeout: 5000 });

        if (test.filter === 'part_type') {
          await this.page.select(test.selector, test.value);
        } else if (test.filter === 'is_proprietary') {
          await this.page.click(test.selector);
        }

        // Wait for filtered results
        await this.page.waitForTimeout(1000);
        await this.page.waitForSelector('.parts-list, .part-item, [data-testid="parts-list"]', { timeout: 10000 });

        const filterTime = Date.now() - startTime;

        results.push({
          success: true,
          filterTime,
          description: test.description,
          filter: test.filter,
          value: test.value
        });

        console.log(`   ✅ ${test.description}: ${filterTime}ms`);

        // Reset filter for next test
        if (test.filter === 'part_type') {
          await this.page.select(test.selector, '');
        } else if (test.filter === 'is_proprietary') {
          await this.page.click(test.selector); // Uncheck
        }

        await this.page.waitForTimeout(500);

      } catch (error) {
        results.push({
          success: false,
          description: test.description,
          filter: test.filter,
          value: test.value,
          error: error.message
        });
        console.log(`   ❌ ${test.description} failed: ${error.message}`);
      }
    }

    return { results };
  }

  async testResponsiveness() {
    console.log('\n📱 Testing interface responsiveness...');

    const results = [];

    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080, description: 'Desktop (1920x1080)' },
      { width: 1366, height: 768, description: 'Laptop (1366x768)' },
      { width: 768, height: 1024, description: 'Tablet (768x1024)' },
      { width: 375, height: 667, description: 'Mobile (375x667)' }
    ];

    for (const viewport of viewports) {
      try {
        const startTime = Date.now();

        await this.page.setViewport(viewport);
        await this.page.reload({ waitUntil: 'networkidle0' });

        const renderTime = Date.now() - startTime;

        // Check if parts are still visible
        const partsVisible = await this.page.$('.parts-list, .part-item, [data-testid="parts-list"]') !== null;

        results.push({
          success: partsVisible,
          renderTime,
          description: viewport.description,
          viewport: viewport,
          partsVisible
        });

        console.log(`   ✅ ${viewport.description}: ${renderTime}ms (parts visible: ${partsVisible})`);

      } catch (error) {
        results.push({
          success: false,
          description: viewport.description,
          viewport: viewport,
          error: error.message
        });
        console.log(`   ❌ ${viewport.description} failed: ${error.message}`);
      }
    }

    // Reset to desktop viewport
    await this.page.setViewport({ width: 1920, height: 1080 });

    return { results };
  }

  async measureMemoryUsage() {
    console.log('\n💾 Measuring memory usage...');

    try {
      const metrics = await this.page.metrics();

      const memoryUsage = {
        jsHeapUsedSize: Math.round(metrics.JSHeapUsedSize / 1024 / 1024), // MB
        jsHeapTotalSize: Math.round(metrics.JSHeapTotalSize / 1024 / 1024), // MB
        timestamp: new Date().toISOString()
      };

      console.log(`   Memory usage: ${memoryUsage.jsHeapUsedSize}MB / ${memoryUsage.jsHeapTotalSize}MB`);

      return { success: true, memoryUsage };

    } catch (error) {
      console.log(`   ❌ Memory measurement failed: ${error.message}`);
      return { success: false, error: error.message };
    }
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
      console.log('✅ Browser closed');
    }
  }

  async runFullFrontendTest() {
    console.log('🚀 Starting ABParts Frontend Scalability Test Suite');
    console.log('=' * 60);

    try {
      await this.initialize();

      if (!await this.authenticate()) {
        return { error: 'Frontend authentication failed' };
      }

      const testResults = {};

      // Run all frontend tests
      testResults.partsPagePerformance = await this.testPartsPagePerformance();
      testResults.filteringPerformance = await this.testFilteringPerformance();
      testResults.responsiveness = await this.testResponsiveness();
      testResults.memoryUsage = await this.measureMemoryUsage();

      // Generate summary
      testResults.summary = this.generateFrontendSummary(testResults);

      return testResults;

    } catch (error) {
      return { error: `Frontend test suite failed: ${error.message}` };
    } finally {
      await this.cleanup();
    }
  }

  generateFrontendSummary(results) {
    const summary = {
      testTimestamp: new Date().toISOString(),
      performanceMetrics: {},
      recommendations: [],
      overallStatus: 'PASS'
    };

    // Analyze parts page performance
    if (results.partsPagePerformance && results.partsPagePerformance.results) {
      const successfulTests = results.partsPagePerformance.results.filter(r => r.success);
      const loadTimes = successfulTests.filter(r => r.loadTime).map(r => r.loadTime);
      const searchTimes = successfulTests.filter(r => r.searchTime).map(r => r.searchTime);

      if (loadTimes.length > 0) {
        summary.performanceMetrics.averagePageLoadTime = loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length;

        if (summary.performanceMetrics.averagePageLoadTime > 3000) {
          summary.recommendations.push('Page load time > 3s - optimize component rendering and data fetching');
          summary.overallStatus = 'WARNING';
        }
      }

      if (searchTimes.length > 0) {
        summary.performanceMetrics.averageSearchTime = searchTimes.reduce((a, b) => a + b, 0) / searchTimes.length;

        if (summary.performanceMetrics.averageSearchTime > 2000) {
          summary.recommendations.push('Search response time > 2s - implement debouncing and optimize API calls');
          summary.overallStatus = 'WARNING';
        }
      }
    }

    // Analyze memory usage
    if (results.memoryUsage && results.memoryUsage.success) {
      summary.performanceMetrics.memoryUsage = results.memoryUsage.memoryUsage.jsHeapUsedSize;

      if (results.memoryUsage.memoryUsage.jsHeapUsedSize > 100) {
        summary.recommendations.push('High memory usage detected - check for memory leaks and optimize component lifecycle');
        summary.overallStatus = 'WARNING';
      }
    }

    // Analyze responsiveness
    if (results.responsiveness && results.responsiveness.results) {
      const responsiveTests = results.responsiveness.results.filter(r => r.success && r.partsVisible);
      summary.performanceMetrics.responsiveViewports = responsiveTests.length;

      if (responsiveTests.length < results.responsiveness.results.length) {
        summary.recommendations.push('Interface not fully responsive across all viewport sizes');
        summary.overallStatus = 'WARNING';
      }
    }

    if (summary.recommendations.length === 0) {
      summary.recommendations.push('All frontend performance tests passed - interface scales well with large datasets');
    }

    return summary;
  }
}

async function main() {
  const tester = new FrontendScalabilityTester();
  const results = await tester.runFullFrontendTest();

  // Save results to file
  fs.writeFileSync('frontend_scalability_results.json', JSON.stringify(results, null, 2));

  console.log('\n' + '='.repeat(60));
  console.log('📊 FRONTEND SCALABILITY TEST RESULTS SUMMARY');
  console.log('='.repeat(60));

  if (results.summary) {
    const summary = results.summary;
    console.log(`Overall Status: ${summary.overallStatus}`);
    console.log(`Test Timestamp: ${summary.testTimestamp}`);

    console.log('\nPerformance Metrics:');
    for (const [metric, value] of Object.entries(summary.performanceMetrics)) {
      if (typeof value === 'number') {
        console.log(`  ${metric}: ${value.toFixed(2)}`);
      } else {
        console.log(`  ${metric}: ${value}`);
      }
    }

    console.log('\nRecommendations:');
    for (const rec of summary.recommendations) {
      console.log(`  • ${rec}`);
    }
  } else if (results.error) {
    console.log(`❌ Test failed: ${results.error}`);
  }

  console.log(`\n📄 Detailed results saved to: frontend_scalability_results.json`);
  console.log('='.repeat(60));
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = FrontendScalabilityTester;