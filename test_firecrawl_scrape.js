/**
 * Test script for firecrawl_scrape MCP tool
 * 
 * This script demonstrates how to use the firecrawl_scrape tool
 * to extract content from websites in different formats.
 */

// Example 1: Basic usage - Extract content in markdown format
async function testBasicScrape() {
  console.log("Example 1: Basic scraping with markdown format");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["markdown"]
    });

    console.log("✅ Success! Content extracted in markdown format");
    console.log("Title:", result.title);
    console.log("Content preview:", result.markdown.substring(0, 200) + "...");
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 2: Extract links from a page
async function testLinkExtraction() {
  console.log("Example 2: Extracting links from a page");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://news.ycombinator.com",
      formats: ["links"]
    });

    console.log("✅ Success! Links extracted");
    console.log("Number of links found:", result.links.length);

    // Display the first 5 links
    console.log("First 5 links:");
    result.links.slice(0, 5).forEach((link, i) => {
      console.log(`${i + 1}. ${link.text || 'No text'}: ${link.url}`);
    });
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 3: Take a screenshot of a page
async function testScreenshotCapture() {
  console.log("Example 3: Capturing a screenshot");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["screenshot"]
    });

    console.log("✅ Success! Screenshot captured");
    console.log("Screenshot data is available as base64");
    console.log("Screenshot data length:", result.screenshot.length);
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 4: Advanced options
async function testAdvancedOptions() {
  console.log("Example 4: Using advanced options");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://example.com",
      formats: ["markdown", "links"],
      maxAge: 3600000, // Use cached results if available and less than 1 hour old
      onlyMainContent: true, // Extract only the main content
      waitFor: 2000, // Wait 2 seconds for dynamic content to load
      mobile: false, // Use desktop viewport
      removeBase64Images: true // Remove base64 encoded images from output
    });

    console.log("✅ Success! Content extracted with advanced options");
    console.log("Content preview:", result.markdown.substring(0, 200) + "...");
    console.log("Number of links:", result.links.length);
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 5: Custom actions before scraping
async function testCustomActions() {
  console.log("Example 5: Using custom actions before scraping");

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

    console.log("✅ Success! Content extracted after custom actions");
    console.log("Content preview:", result.markdown.substring(0, 200) + "...");
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Run all examples
async function runAllExamples() {
  console.log("Starting firecrawl_scrape tests...\n");

  await testBasicScrape();
  await testLinkExtraction();
  await testScreenshotCapture();
  await testAdvancedOptions();
  await testCustomActions();

  console.log("All tests completed!");
}

// Execute the tests
runAllExamples().catch(error => {
  console.error("Error running tests:", error);
});