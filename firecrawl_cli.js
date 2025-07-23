#!/usr/bin/env node

/**
 * Firecrawl CLI Test Script
 * 
 * This script demonstrates how to use the firecrawl_scrape tool from the command line.
 * It's designed to be run with Node.js and requires the firecrawl-mcp package.
 * 
 * Usage:
 *   node firecrawl_cli.js <url> [format1,format2,...]
 * 
 * Example:
 *   node firecrawl_cli.js https://example.com markdown,links
 */

// Import required modules
const { createClient } = require('firecrawl-mcp');

// Parse command line arguments
const args = process.argv.slice(2);
const url = args[0] || 'https://example.com';
const formatsArg = args[1] || 'markdown';
const formats = formatsArg.split(',').map(f => f.trim());

// Create a client
const client = createClient({
  apiKey: process.env.FIRECRAWL_API_KEY || 'YOUR-API-KEY'
});

// Display info
console.log(`Scraping URL: ${url}`);
console.log(`Formats: ${formats.join(', ')}`);
console.log('');

// Perform the scrape
async function scrapeWebsite() {
  try {
    console.log('Scraping website...');

    const result = await client.scrape({
      url,
      formats
    });

    console.log('\nScrape successful!');
    console.log(`Title: ${result.title || 'Unknown'}`);

    // Display results based on requested formats
    if (result.markdown) {
      console.log('\n--- Markdown Content Preview ---');
      console.log(result.markdown.substring(0, 500) + (result.markdown.length > 500 ? '...' : ''));
    }

    if (result.links && result.links.length > 0) {
      console.log(`\n--- Links (${result.links.length}) ---`);
      result.links.slice(0, 10).forEach((link, i) => {
        console.log(`${i + 1}. ${link.text || 'No text'}: ${link.url}`);
      });
      if (result.links.length > 10) {
        console.log(`... and ${result.links.length - 10} more`);
      }
    }

    if (result.html) {
      console.log('\n--- HTML Content Preview ---');
      console.log(result.html.substring(0, 200) + '...');
    }

    if (result.screenshot) {
      console.log('\n--- Screenshot captured ---');
      console.log('Screenshot data is available as base64');
    }

  } catch (error) {
    console.error('Error scraping website:', error);
    process.exit(1);
  }
}

// Check if we're in a real Node.js environment
if (typeof require !== 'undefined') {
  // This is a real Node.js environment
  console.log('Note: This script requires the firecrawl-mcp package to be installed.');
  console.log('If you get module not found errors, install it with: npm install firecrawl-mcp\n');

  // Run the scrape
  scrapeWebsite().catch(console.error);
} else {
  // This is being run in a browser or other environment
  console.log('This script is designed to be run with Node.js');
}