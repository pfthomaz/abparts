# Testing Firecrawl MCP Tools

This repository contains scripts and guides for testing the Firecrawl MCP tools, particularly the `firecrawl_scrape` tool.

## Overview

The Firecrawl MCP server provides powerful web scraping and data extraction capabilities through several tools:

- `firecrawl_scrape` - Scrape content from a single URL
- `firecrawl_map` - Map a website to discover all indexed URLs
- `firecrawl_search` - Search the web for specific information
- `firecrawl_extract` - Extract structured information from web pages

## Getting Started

### 1. Set Up Your API Key

Before you can use the Firecrawl MCP tools, you need to set up your API key:

```bash
# Run the update script with your API key
node update_firecrawl_api_key.js YOUR-API-KEY
```

Alternatively, you can manually edit the `.kiro/settings/mcp.json` file and replace `"YOUR-API-KEY"` with your actual API key.

### 2. Restart MCP Servers

After updating your API key, restart the MCP servers:

1. Open the Kiro command palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Search for "MCP: Restart Servers"
3. Select this command to restart the MCP servers

### 3. Run the Quick Start Example

Try the quick start example to test basic functionality:

```javascript
// In Kiro, open firecrawl_quick_start.js and run it
```

### 4. Explore More Examples

Once the basic example is working, explore more advanced examples:

- `firecrawl_examples.js` - Comprehensive examples of all Firecrawl tools
- `firecrawl_test.html` - Interactive HTML page for testing in a browser

## Testing firecrawl_scrape

The `firecrawl_scrape` tool is particularly useful for extracting content from websites. Here's a simple example:

```javascript
// Basic usage
const result = await mcp_firecrawl_mcp_firecrawl_scrape({
  url: "https://example.com",
  formats: ["markdown"]
});

console.log(result.markdown);
```

### Available Options

The `firecrawl_scrape` tool supports many options:

- `url` - The URL to scrape
- `formats` - Content formats to extract (markdown, html, rawHtml, screenshot, links)
- `maxAge` - Maximum age in milliseconds for cached content
- `onlyMainContent` - Extract only the main content
- `waitFor` - Time in milliseconds to wait for dynamic content to load
- `mobile` - Use mobile viewport
- `location` - Location settings for geolocation
- `excludeTags` - HTML tags to exclude
- `includeTags` - HTML tags to specifically include

## Troubleshooting

If you encounter a 401 Unauthorized error, it means your API key is invalid or not properly configured. Make sure you've:

1. Obtained a valid API key from Firecrawl
2. Updated your MCP configuration with the correct API key
3. Restarted the MCP servers

For more detailed instructions, see the `FIRECRAWL_SETUP_GUIDE.md` file.

## Files in this Repository

- `firecrawl_quick_start.js` - Simple script to test basic functionality
- `firecrawl_examples.js` - Comprehensive examples of all Firecrawl tools
- `firecrawl_test.html` - Interactive HTML page for testing in a browser
- `firecrawl_cli.js` - Command-line script for testing
- `update_firecrawl_api_key.js` - Script to update your API key
- `FIRECRAWL_SETUP_GUIDE.md` - Detailed setup instructions
- `README.md` - This file