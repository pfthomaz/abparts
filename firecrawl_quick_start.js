/**
 * Firecrawl MCP Quick Start Guide
 * 
 * This file demonstrates how to use the firecrawl_scrape tool from the firecrawl-mcp server.
 * Before running this, make sure to update your API key in .kiro/settings/mcp.json
 */

// Step 1: Update your API key in .kiro/settings/mcp.json
// Replace "YOUR-API-KEY" with your actual Firecrawl API key

// Step 2: Basic website scraping
async function basicScrape() {
  try {
    console.log("Scraping example.com with firecrawl_scrape...");

    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["markdown"]
    });

    console.log("Scrape successful!");
    console.log("Title:", result.title);
    console.log("Content:", result.markdown.substring(0, 200) + "...");

    return result;
  } catch (error) {
    console.error("Error during scrape:", error);
    console.log("\nTroubleshooting tips:");
    console.log("1. Make sure you've updated your API key in .kiro/settings/mcp.json");
    console.log("2. Check that the firecrawl-mcp server is running");
    console.log("3. Verify that the URL you're trying to scrape is accessible");

    throw error;
  }
}

// Step 3: Advanced scraping with multiple formats and options
async function advancedScrape() {
  try {
    console.log("\nPerforming advanced scrape with multiple formats...");

    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://news.ycombinator.com",
      formats: ["markdown", "links", "screenshot"],
      maxAge: 3600000, // Use cached results if available and less than 1 hour old
      onlyMainContent: true, // Extract only the main content
      waitFor: 2000 // Wait 2 seconds for dynamic content to load
    });

    console.log("Advanced scrape successful!");
    console.log("Number of links found:", result.links ? result.links.length : 0);

    if (result.links && result.links.length > 0) {
      console.log("\nSample links:");
      result.links.slice(0, 5).forEach((link, i) => {
        console.log(`${i + 1}. ${link.text || "No text"}: ${link.url}`);
      });
    }

    return result;
  } catch (error) {
    console.error("Error during advanced scrape:", error);
    throw error;
  }
}

// Step 4: Run the examples
async function runExamples() {
  try {
    // Run basic scrape
    const basicResult = await basicScrape();

    // Run advanced scrape
    const advancedResult = await advancedScrape();

    console.log("\nAll examples completed successfully!");

    // Return the results for further inspection
    return {
      basicResult,
      advancedResult
    };
  } catch (error) {
    console.error("\nFailed to run examples:", error);
  }
}

// Execute the examples
runExamples();

/**
 * Additional firecrawl_scrape options:
 * 
 * url: "https://example.com" - The URL to scrape
 * formats: ["markdown", "html", "rawHtml", "screenshot", "links"] - Content formats to extract
 * maxAge: 3600000 - Maximum age in milliseconds for cached content
 * onlyMainContent: true - Extract only the main content
 * waitFor: 2000 - Time in milliseconds to wait for dynamic content to load
 * mobile: true - Use mobile viewport
 * location: { country: "US", languages: ["en"] } - Location settings
 * excludeTags: ["script", "style"] - HTML tags to exclude
 * includeTags: ["article", "main"] - HTML tags to specifically include
 * removeBase64Images: true - Remove base64 encoded images from output
 * timeout: 30000 - Maximum time in milliseconds to wait for the page to load
 */