// Test script for firecrawl_scrape MCP tool

// Example website to scrape
const testUrl = "https://example.com";

// Let's test the firecrawl_scrape tool
console.log(`Testing firecrawl_scrape on ${testUrl}...`);

// The tool should be available through the MCP server
// Let's try to scrape the website and get its content in markdown format
mcp_firecrawl_mcp_firecrawl_scrape({
  url: testUrl,
  formats: ["markdown"]
})
  .then(result => {
    console.log("Scrape successful!");
    console.log("Website title:", result.title || "Unknown");
    console.log("Content length:", (result.markdown || "").length);
    console.log("\nFirst 300 characters of content:");
    console.log((result.markdown || "").substring(0, 300));
  })
  .catch(error => {
    console.error("Error scraping website:", error);
  });

// Let's also try to get HTML content and links
console.log("\nTesting with multiple formats...");
mcp_firecrawl_mcp_firecrawl_scrape({
  url: testUrl,
  formats: ["html", "links"]
})
  .then(result => {
    console.log("Multiple formats scrape successful!");
    console.log("Number of links found:", (result.links || []).length);
    console.log("\nFirst 3 links (if any):");
    (result.links || []).slice(0, 3).forEach(link => {
      console.log(`- ${link.text || "No text"}: ${link.url}`);
    });
  })
  .catch(error => {
    console.error("Error scraping with multiple formats:", error);
  });