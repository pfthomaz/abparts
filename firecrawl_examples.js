/**
 * Firecrawl MCP Tools Examples
 * 
 * This file demonstrates how to use the various tools provided by the firecrawl-mcp server.
 * Each example shows a different capability of the scraping tools.
 */

// First, let's check if your API key is properly set
console.log("Checking Firecrawl MCP configuration...");
// Note: The API key should be set in your .kiro/settings/mcp.json file

// Example 1: Basic website scraping with firecrawl_scrape
async function testBasicScrape() {
  console.log("\n=== Example 1: Basic Website Scraping ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["markdown"]
    });

    console.log("✅ Basic scrape successful");
    console.log(`Title: ${result.title || "Unknown"}`);
    console.log(`Content preview: ${(result.markdown || "").substring(0, 100)}...`);
  } catch (error) {
    console.error("❌ Basic scrape failed:", error);
  }
}

// Example 2: Scraping with multiple formats
async function testMultipleFormats() {
  console.log("\n=== Example 2: Scraping with Multiple Formats ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://news.ycombinator.com",
      formats: ["markdown", "links", "screenshot"]
    });

    console.log("✅ Multiple formats scrape successful");
    console.log(`Content length: ${(result.markdown || "").length} characters`);
    console.log(`Number of links: ${(result.links || []).length}`);
    console.log(`Screenshot captured: ${result.screenshot ? "Yes" : "No"}`);

    // Display some links
    if (result.links && result.links.length > 0) {
      console.log("\nSample links:");
      result.links.slice(0, 3).forEach((link, i) => {
        console.log(`${i + 1}. ${link.text || "No text"}: ${link.url}`);
      });
    }
  } catch (error) {
    console.error("❌ Multiple formats scrape failed:", error);
  }
}

// Example 3: Scraping with custom actions
async function testCustomActions() {
  console.log("\n=== Example 3: Scraping with Custom Actions ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["markdown"],
      actions: [
        { type: "wait", milliseconds: 1000 },
        { type: "scroll", direction: "down" },
        { type: "wait", milliseconds: 500 },
        { type: "screenshot", fullPage: true }
      ]
    });

    console.log("✅ Custom actions scrape successful");
    console.log(`Content after actions: ${(result.markdown || "").substring(0, 100)}...`);
  } catch (error) {
    console.error("❌ Custom actions scrape failed:", error);
  }
}

// Example 4: Mapping a website to discover URLs
async function testWebsiteMapping() {
  console.log("\n=== Example 4: Website Mapping ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_map({
      url: "https://example.com",
      limit: 10
    });

    console.log("✅ Website mapping successful");
    console.log(`URLs discovered: ${result.urls.length}`);

    if (result.urls.length > 0) {
      console.log("\nDiscovered URLs:");
      result.urls.forEach((url, i) => {
        console.log(`${i + 1}. ${url}`);
      });
    }
  } catch (error) {
    console.error("❌ Website mapping failed:", error);
  }
}

// Example 5: Searching the web
async function testWebSearch() {
  console.log("\n=== Example 5: Web Search ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_search({
      query: "web scraping tools",
      limit: 5
    });

    console.log("✅ Web search successful");
    console.log(`Search results: ${result.results.length}`);

    if (result.results.length > 0) {
      console.log("\nSearch results:");
      result.results.forEach((item, i) => {
        console.log(`${i + 1}. ${item.title} - ${item.url}`);
      });
    }
  } catch (error) {
    console.error("❌ Web search failed:", error);
  }
}

// Example 6: Extracting structured data
async function testStructuredDataExtraction() {
  console.log("\n=== Example 6: Structured Data Extraction ===");
  try {
    const result = await mcp_firecrawl_mcp_firecrawl_extract({
      urls: ["https://example.com"],
      prompt: "Extract the main heading and any subheadings from this page",
      schema: {
        type: "object",
        properties: {
          mainHeading: { type: "string" },
          subHeadings: { type: "array", items: { type: "string" } }
        }
      }
    });

    console.log("✅ Structured data extraction successful");
    console.log("Extracted data:", JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error("❌ Structured data extraction failed:", error);
  }
}

// Run all examples
async function runAllExamples() {
  console.log("Starting Firecrawl MCP examples...");

  // Check if the API key is set to a real value
  const configFile = ".kiro/settings/mcp.json";
  try {
    const config = require(configFile);
    const apiKey = config.mcpServers["firecrawl-mcp"]?.env?.FIRECRAWL_API_KEY;

    if (!apiKey || apiKey === "YOUR-API-KEY") {
      console.error("⚠️ Warning: You need to set a real API key in .kiro/settings/mcp.json");
      console.error("The examples may not work without a valid API key.");
    }
  } catch (error) {
    console.error("⚠️ Could not check API key configuration:", error.message);
  }

  // Run the examples
  await testBasicScrape();
  await testMultipleFormats();
  await testCustomActions();
  await testWebsiteMapping();
  await testWebSearch();
  await testStructuredDataExtraction();

  console.log("\n✨ All examples completed!");
}

// Run the examples
runAllExamples().catch(error => {
  console.error("Error running examples:", error);
});