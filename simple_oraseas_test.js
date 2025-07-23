/**
 * Simple test for firecrawl_scrape with Oraseas website
 */

// Simple function to test firecrawl_scrape
async function testFirecrawlScrape() {
  console.log("Testing firecrawl_scrape with Oraseas website...");

  try {
    // Call the firecrawl_scrape tool
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["markdown", "links"]
    });

    // Log the results
    console.log("Success! Here are the results:");
    console.log("Title:", result.title);

    if (result.markdown) {
      console.log("\nMarkdown content preview:");
      console.log(result.markdown.substring(0, 500) + "...");
    }

    if (result.links && result.links.length > 0) {
      console.log("\nLinks found:", result.links.length);
      console.log("First 10 links:");

      result.links.slice(0, 10).forEach((link, i) => {
        console.log(`${i + 1}. ${link.text || 'No text'}: ${link.url}`);
      });
    }

    return result;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
}

// Run the test
testFirecrawlScrape()
  .then(result => {
    console.log("\nTest completed successfully!");
  })
  .catch(error => {
    console.error("\nTest failed:", error);
  });