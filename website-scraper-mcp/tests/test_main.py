"""Tests for the main module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.main import WebScraperMCPServer
from website_scraper_mcp.models import ScrapingResult


class TestWebScraperMCPServer(unittest.TestCase):
    """Test the WebScraperMCPServer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.server = WebScraperMCPServer()
        self.server.orchestrator = MagicMock()
        self.server.orchestrator.scrape = AsyncMock()

    def test_register_tools(self):
        """Test registering MCP tools."""
        tools = self.server.register_tools()
        
        # Verify tools were registered
        self.assertEqual(len(tools), 4)
        
        # Verify tool names
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("scrape_website", tool_names)
        self.assertIn("extract_logo", tool_names)
        self.assertIn("extract_colors", tool_names)
        self.assertIn("extract_ui_styles", tool_names)
        
        # Verify parameters
        scrape_tool = next(tool for tool in tools if tool["name"] == "scrape_website")
        self.assertIn("url", scrape_tool["parameters"]["properties"])
        self.assertIn("elements", scrape_tool["parameters"]["properties"])
        self.assertIn("selectors", scrape_tool["parameters"]["properties"])
        self.assertIn("options", scrape_tool["parameters"]["properties"])

    async def test_handle_request_unknown_tool(self):
        """Test handling an unknown tool request."""
        result = await self.server.handle_request("unknown_tool", {"url": "https://example.com"})
        
        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Unknown tool", result["error"])

    async def test_handle_request_missing_url(self):
        """Test handling a request with missing URL."""
        result = await self.server.handle_request("scrape_website", {})
        
        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Missing required parameter: url", result["error"])

    async def test_handle_request_invalid_url(self):
        """Test handling a request with invalid URL."""
        result = await self.server.handle_request("scrape_website", {"url": ""})
        
        # Verify error response
        self.assertIn("error", result)
        self.assertIn("Invalid URL parameter", result["error"])

    async def test_handle_scrape_website(self):
        """Test handling a scrape_website request."""
        # Mock orchestrator.scrape to return a result
        mock_result = ScrapingResult(
            url="https://example.com",
            logos=[MagicMock()],
            colors=[MagicMock()],
            ui_style=MagicMock(),
        )
        self.server.orchestrator.scrape.return_value = mock_result
        
        # Call handle_request
        result = await self.server.handle_request("scrape_website", {
            "url": "https://example.com",
            "elements": ["logos", "colors", "styles"],
            "selectors": {"logo": ".logo"},
            "options": {"browser_type": "chromium"},
        })
        
        # Verify orchestrator.scrape was called with correct parameters
        self.server.orchestrator.scrape.assert_called_once()
        request = self.server.orchestrator.scrape.call_args[0][0]
        self.assertEqual(request.url, "https://example.com")
        self.assertEqual(request.elements, ["logos", "colors", "styles"])
        self.assertEqual(request.selectors, {"logo": ".logo"})
        self.assertEqual(request.options, {"browser_type": "chromium"})
        
        # Verify result
        self.assertEqual(result, mock_result.dict(exclude_none=True))

    async def test_handle_extract_logo(self):
        """Test handling an extract_logo request."""
        # Mock orchestrator.scrape to return a result with logos
        mock_logos = [MagicMock(), MagicMock()]
        mock_result = ScrapingResult(
            url="https://example.com",
            logos=mock_logos,
        )
        self.server.orchestrator.scrape.return_value = mock_result
        
        # Call handle_request
        result = await self.server.handle_request("extract_logo", {
            "url": "https://example.com",
            "selector": ".logo",
        })
        
        # Verify orchestrator.scrape was called with correct parameters
        self.server.orchestrator.scrape.assert_called_once()
        request = self.server.orchestrator.scrape.call_args[0][0]
        self.assertEqual(request.url, "https://example.com")
        self.assertEqual(request.elements, ["logos"])
        self.assertEqual(request.selectors, {"logo": ".logo"})
        
        # Verify result
        self.assertEqual(result["logos"], mock_logos)

    async def test_handle_extract_logo_no_logos_found(self):
        """Test handling an extract_logo request when no logos are found."""
        # Mock orchestrator.scrape to return a result with no logos
        mock_result = ScrapingResult(
            url="https://example.com",
            logos=None,
        )
        self.server.orchestrator.scrape.return_value = mock_result
        
        # Call handle_request
        result = await self.server.handle_request("extract_logo", {
            "url": "https://example.com",
        })
        
        # Verify result has an error
        self.assertIn("error", result)
        self.assertIn("No logos found", result["error"])

    async def test_handle_extract_colors(self):
        """Test handling an extract_colors request."""
        # Mock orchestrator.scrape to return a result with colors
        mock_colors = [MagicMock(), MagicMock()]
        mock_palette = {"primary": [mock_colors[0]], "secondary": [mock_colors[1]]}
        mock_result = ScrapingResult(
            url="https://example.com",
            colors=mock_colors,
            color_palette=mock_palette,
        )
        self.server.orchestrator.scrape.return_value = mock_result
        
        # Call handle_request
        result = await self.server.handle_request("extract_colors", {
            "url": "https://example.com",
            "element_focus": "buttons",
        })
        
        # Verify orchestrator.scrape was called with correct parameters
        self.server.orchestrator.scrape.assert_called_once()
        request = self.server.orchestrator.scrape.call_args[0][0]
        self.assertEqual(request.url, "https://example.com")
        self.assertEqual(request.elements, ["colors"])
        self.assertEqual(request.options, {"element_focus": "buttons"})
        
        # Verify result
        self.assertEqual(result["colors"], mock_colors)
        self.assertEqual(result["color_palette"], mock_palette)

    async def test_handle_extract_ui_styles(self):
        """Test handling an extract_ui_styles request."""
        # Mock orchestrator.scrape to return a result with UI styles
        mock_ui_style = MagicMock()
        mock_result = ScrapingResult(
            url="https://example.com",
            ui_style=mock_ui_style,
        )
        self.server.orchestrator.scrape.return_value = mock_result
        
        # Call handle_request
        result = await self.server.handle_request("extract_ui_styles", {
            "url": "https://example.com",
            "component_types": ["button", "form"],
        })
        
        # Verify orchestrator.scrape was called with correct parameters
        self.server.orchestrator.scrape.assert_called_once()
        request = self.server.orchestrator.scrape.call_args[0][0]
        self.assertEqual(request.url, "https://example.com")
        self.assertEqual(request.elements, ["styles"])
        self.assertEqual(request.options, {"component_types": ["button", "form"]})
        
        # Verify result
        self.assertEqual(result["ui_style"], mock_ui_style)


if __name__ == "__main__":
    # Run tests
    unittest.main()