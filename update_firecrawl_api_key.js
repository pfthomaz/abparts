/**
 * Update Firecrawl API Key
 * 
 * This script updates the Firecrawl API key in your MCP configuration.
 * Run it with Node.js and provide your API key as an argument.
 * 
 * Usage:
 *   node update_firecrawl_api_key.js YOUR-API-KEY
 */

const fs = require('fs');
const path = require('path');

// Get API key from command line argument
const apiKey = process.argv[2];

if (!apiKey) {
  console.error('Error: No API key provided');
  console.log('Usage: node update_firecrawl_api_key.js YOUR-API-KEY');
  process.exit(1);
}

// Path to MCP configuration file
const configPath = path.join('.kiro', 'settings', 'mcp.json');

// Read current configuration
try {
  const configData = fs.readFileSync(configPath, 'utf8');
  const config = JSON.parse(configData);

  // Update API key
  if (config.mcpServers && config.mcpServers['firecrawl-mcp']) {
    config.mcpServers['firecrawl-mcp'].env = config.mcpServers['firecrawl-mcp'].env || {};
    config.mcpServers['firecrawl-mcp'].env.FIRECRAWL_API_KEY = apiKey;

    // Write updated configuration
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

    console.log('API key updated successfully!');
    console.log('Remember to restart your MCP servers for the changes to take effect.');
  } else {
    console.error('Error: firecrawl-mcp server not found in configuration');
    console.log('Make sure your MCP configuration includes the firecrawl-mcp server.');
  }
} catch (error) {
  console.error('Error updating API key:', error.message);

  if (error.code === 'ENOENT') {
    console.log('The MCP configuration file was not found.');
    console.log('Creating a new configuration file with the firecrawl-mcp server...');

    // Create directory if it doesn't exist
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }

    // Create new configuration
    const newConfig = {
      mcpServers: {
        'firecrawl-mcp': {
          command: 'npx',
          args: ['-y', 'firecrawl-mcp'],
          env: {
            FIRECRAWL_API_KEY: apiKey
          }
        }
      }
    };

    // Write new configuration
    fs.writeFileSync(configPath, JSON.stringify(newConfig, null, 2));

    console.log('New MCP configuration created successfully!');
    console.log('Remember to restart your MCP servers for the changes to take effect.');
  }
}