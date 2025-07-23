# Website Scraper MCP

A Model Context Protocol (MCP) server for scraping websites to extract logos, UI styling, and color palettes.

## Features

- Extract logos from websites
- Extract color palettes and dominant colors
- Extract UI styling information (typography, spacing, components)
- Detect CSS frameworks
- Export results in multiple formats

## Installation

```bash
pip install website-scraper-mcp
```

## Usage with Kiro

1. Add the MCP server to your Kiro configuration:

```json
{
  "mcpServers": {
    "website-scraper": {
      "command": "uvx",
      "args": ["website-scraper-mcp@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["extract_logo", "extract_colors", "extract_ui_styles"]
    }
  }
}
```

2. Use the MCP tools in Kiro:

```
# Extract logo from a website
extract_logo("https://example.com")

# Extract color palette from a website
extract_colors("https://example.com")

# Extract UI styling from a website
extract_ui_styles("https://example.com")

# Extract all elements from a website
scrape_website("https://example.com", elements=["logos", "colors", "styles"])
```

## Development

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`

## License

MIT