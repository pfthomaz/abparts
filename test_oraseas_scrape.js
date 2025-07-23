/**
 * Test script for firecrawl_scrape MCP tool using Oraseas website
 * 
 * This script demonstrates how to use the firecrawl_scrape tool
 * to extract content from the Oraseas website in different formats.
 */

// Example 1: Basic usage - Extract content in markdown format
async function testBasicScrape() {
  console.log("Example 1: Basic scraping with markdown format");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
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

// Example 2: Extract links from the Oraseas website
async function testLinkExtraction() {
  console.log("Example 2: Extracting links from the Oraseas website");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
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

// Example 3: Take a screenshot of the Oraseas website
async function testScreenshotCapture() {
  console.log("Example 3: Capturing a screenshot of the Oraseas website");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["screenshot"]
    });

    console.log("✅ Success! Screenshot captured");
    console.log("Screenshot data is available as base64");
    console.log("Screenshot data length:", result.screenshot ? result.screenshot.length : "N/A");
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 4: Advanced options with Oraseas website
async function testAdvancedOptions() {
  console.log("Example 4: Using advanced options with Oraseas website");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["markdown", "links"],
      maxAge: 3600000, // Use cached results if available and less than 1 hour old
      onlyMainContent: true, // Extract only the main content
      waitFor: 2000, // Wait 2 seconds for dynamic content to load
      mobile: false, // Use desktop viewport
      removeBase64Images: true // Remove base64 encoded images from output
    });

    console.log("✅ Success! Content extracted with advanced options");
    console.log("Content preview:", result.markdown.substring(0, 200) + "...");
    console.log("Number of links:", result.links ? result.links.length : 0);
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 5: Custom actions before scraping Oraseas website
async function testCustomActions() {
  console.log("Example 5: Using custom actions before scraping Oraseas website");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
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

// Example 6: Extract HTML content from Oraseas website
async function testHtmlExtraction() {
  console.log("Example 6: Extracting HTML content from Oraseas website");

  try {
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["html"]
    });

    console.log("✅ Success! HTML content extracted");
    console.log("HTML content length:", result.html ? result.html.length : 0);
    console.log("HTML content preview:", (result.html || "").substring(0, 200) + "...");
    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Example 7: Extract specific elements using CSS selectors
async function testSpecificElementExtraction() {
  console.log("Example 7: Extracting specific elements using CSS selectors");

  try {
    // First, let's try to identify some common selectors on the Oraseas website
    // This is a generic approach since we don't know the exact structure
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["markdown"],
      actions: [
        // First, let's try to find the main heading or logo
        {
          type: "scrape",
          selector: "h1, .logo, header img, [class*='logo']",
          name: "mainHeading"
        },
        // Then, let's try to find the main navigation
        {
          type: "scrape",
          selector: "nav, .nav, .menu, header ul",
          name: "navigation"
        },
        // Finally, let's try to find the main content area
        {
          type: "scrape",
          selector: "main, .main, #main, article, .content, #content",
          name: "mainContent"
        }
      ]
    });

    console.log("✅ Success! Specific elements extracted");

    // Check if we got any custom scrape results
    if (result.scrapes) {
      console.log("Custom scrape results:");

      if (result.scrapes.mainHeading) {
        console.log("Main heading:", result.scrapes.mainHeading.substring(0, 100) + "...");
      }

      if (result.scrapes.navigation) {
        console.log("Navigation:", result.scrapes.navigation.substring(0, 100) + "...");
      }

      if (result.scrapes.mainContent) {
        console.log("Main content:", result.scrapes.mainContent.substring(0, 100) + "...");
      }
    } else {
      console.log("No custom scrape results found");
    }

    console.log("\n");
  } catch (error) {
    console.error("❌ Error:", error);
    console.error("\n");
  }
}

// Run all examples
async function runAllExamples() {
  console.log("Starting firecrawl_scrape tests with Oraseas website...\n");

  await testBasicScrape();
  await testLinkExtraction();
  await testScreenshotCapture();
  await testAdvancedOptions();
  await testCustomActions();
  await testHtmlExtraction();
  await testSpecificElementExtraction();

  console.log("All tests completed!");
}

// Execute the tests
runAllExamples().catch(error => {
  console.error("Error running tests:", error);
});