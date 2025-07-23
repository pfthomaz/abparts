# Firecrawl MCP Setup Guide

This guide will help you set up and use the Firecrawl MCP server for web scraping and data extraction.

## 1. Get an API Key

To use the Firecrawl MCP server, you need a valid API key:

1. Visit [Firecrawl's website](https://firecrawl.dev) (or the appropriate provider)
2. Sign up for an account or log in
3. Navigate to your account settings or API section
4. Generate a new API key
5. Copy the API key for the next step

## 2. Update Your MCP Configuration

Update your `.kiro/settings/mcp.json` file with your API key:

```json
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "firecrawl-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

Replace `"your-actual-api-key-here"` with the API key you obtained in step 1.

## 3. Restart the MCP Server

After updating your configuration:

1. Open the Kiro command palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Search for "MCP: Restart Servers"
3. Select this command to restart the MCP servers with your new configuration

## 4. Test the Firecrawl MCP Tools

You can use the provided test scripts to verify your setup:

- `firecrawl_quick_start.js` - A simple script to test basic functionality
- `firecrawl_examples.js` - A comprehensive set of examples for all Firecrawl tools
- `firecrawl_test.html` - An interactive HTML page for testing in a browser

## 5. Available Firecrawl MCP Tools

The Firecrawl MCP server provides several tools:

### firecrawl_scrape

Scrapes content from a single URL:

```javascript
const result = await mcp_firecrawl_mcp_firecrawl_scrape({
  url: "https://example.com",
  formats: ["markdown", "links"]
});
```

### firecrawl_map

Maps a website to discover all indexed URLs:

```javascript
const result = await mcp_firecrawl_mcp_firecrawl_map({
  url: "https://example.com"
});
```

### firecrawl_search

Searches the web for specific information:

```javascript
const result = await mcp_firecrawl_mcp_firecrawl_search({
  query: "web scraping tools",
  limit: 5
});
```

### firecrawl_extract

Extracts structured information from web pages:

```javascript
const result = await mcp_firecrawl_mcp_firecrawl_extract({
  urls: ["https://example.com"],
  prompt: "Extract the main heading and any subheadings",
  schema: {
    type: "object",
    properties: {
      mainHeading: { type: "string" },
      subHeadings: { type: "array", items: { type: "string" } }
    }
  }
});
```

## 6. Troubleshooting

If you encounter issues:

1. **401 Unauthorized Error**: Check that your API key is correct and properly configured
2. **Module Not Found**: Make sure the firecrawl-mcp package is installed
3. **Timeout Errors**: Try increasing the timeout value in your requests
4. **Rate Limiting**: You might be making too many requests; check your API usage limits

For more help, refer to the Firecrawl documentation or contact their support team.