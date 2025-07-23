/**
 * Script to save Oraseas website content to files
 * 
 * This script scrapes the Oraseas website and saves the content to files.
 */

const fs = require('fs');
const path = require('path');

// Create output directory if it doesn't exist
const outputDir = path.join('docs', 'oraseas');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Function to save content to a file
function saveToFile(filename, content) {
  const filePath = path.join(outputDir, filename);
  fs.writeFileSync(filePath, content);
  console.log(`Saved to ${filePath}`);
}

// Function to scrape and save Oraseas website content
async function scrapeAndSaveOraseas() {
  console.log("Scraping Oraseas website...");

  try {
    // Call the firecrawl_scrape tool with multiple formats
    const result = await mcp_firecrawl_mcp_firecrawl_scrape({
      url: "https://oraseas.com/",
      formats: ["markdown", "html", "links", "screenshot"]
    });

    console.log("Scraping successful!");

    // Save the results to files
    if (result.markdown) {
      saveToFile('oraseas-content.md', result.markdown);
    }

    if (result.html) {
      saveToFile('oraseas-content.html', result.html);
    }

    if (result.links) {
      saveToFile('oraseas-links.json', JSON.stringify(result.links, null, 2));
    }

    if (result.screenshot) {
      // Save screenshot as base64 in a text file
      saveToFile('oraseas-screenshot.txt', result.screenshot);

      // Also try to save as an image file
      try {
        const imageBuffer = Buffer.from(result.screenshot, 'base64');
        saveToFile('oraseas-screenshot.png', imageBuffer);
      } catch (error) {
        console.error("Error saving screenshot as image:", error);
      }
    }

    // Save the full result object
    saveToFile('oraseas-webscrape.json', JSON.stringify(result, null, 2));

    console.log("All content saved successfully!");
    return result;
  } catch (error) {
    console.error("Error scraping Oraseas website:", error);
    throw error;
  }
}

// Run the scrape and save function
scrapeAndSaveOraseas()
  .then(() => {
    console.log("Process completed successfully!");
  })
  .catch(error => {
    console.error("Process failed:", error);
  });