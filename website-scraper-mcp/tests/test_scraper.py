"""Tests for the Website Scraper MCP Server."""

import asyncio
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.models import ScrapingRequest, ScrapingResult
from website_scraper_mcp.scraper import ScrapingOrchestrator


class TestScrapingOrchestrator(unittest.TestCase):
    """Test the ScrapingOrchestrator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = ScrapingOrchestrator()
        self.orchestrator.logo_extractor = MagicMock()
        self.orchestrator.color_extractor = MagicMock()
        self.orchestrator.ui_style_extractor = MagicMock()
        self.orchestrator.browser_engine = MagicMock()
        self.orchestrator.validate_url = AsyncMock()

    async def test_scrape_with_cache_hit(self):
        """Test scraping with a cache hit."""
        # Create a request
        request = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors", "styles"],
        )
        
        # Create a cached result
        cached_result = ScrapingResult(
            url="https://example.com",
            logos=[MagicMock()],
            colors=[MagicMock()],
            ui_style=MagicMock(),
        )
        
        # Add to cache
        cache_key = self.orchestrator._get_cache_key(request)
        self.orchestrator._cache[cache_key] = (datetime.now(), cached_result)
        
        # Call scrape
        result = await self.orchestrator.scrape(request)
        
        # Verify validate_url was not called
        self.orchestrator.validate_url.assert_not_called()
        
        # Verify result is the cached result
        self.assertEqual(result, cached_result)

    async def test_scrape_with_cache_miss(self):
        """Test scraping with a cache miss."""
        # Create a request
        request = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors", "styles"],
        )
        
        # Mock _setup_browser_and_navigate
        browser_data = {
            "browser": MagicMock(),
            "context": MagicMock(),
            "page": MagicMock(),
            "soup": MagicMock(),
            "metadata": {"title": "Example"},
        }
        self.orchestrator._setup_browser_and_navigate = AsyncMock(return_value=browser_data)
        
        # Mock _capture_screenshots
        screenshots = {"full": "base64_data", "viewport": "base64_data"}
        self.orchestrator._capture_screenshots = AsyncMock(return_value=screenshots)
        
        # Mock extractors
        self.orchestrator.logo_extractor.extract = AsyncMock(return_value=[MagicMock()])
        self.orchestrator.color_extractor.extract = AsyncMock(return_value={
            "colors": [MagicMock()],
            "palette": {"primary": [MagicMock()]},
        })
        self.orchestrator.ui_style_extractor.extract = AsyncMock(return_value=MagicMock())
        
        # Call scrape
        result = await self.orchestrator.scrape(request)
        
        # Verify validate_url was called
        self.orchestrator.validate_url.assert_called_once_with("https://example.com")
        
        # Verify _setup_browser_and_navigate was called
        self.orchestrator._setup_browser_and_navigate.assert_called_once()
        
        # Verify _capture_screenshots was called
        self.orchestrator._capture_screenshots.assert_called_once_with(browser_data["page"])
        
        # Verify extractors were called
        self.orchestrator.logo_extractor.extract.assert_called_once()
        self.orchestrator.color_extractor.extract.assert_called_once()
        self.orchestrator.ui_style_extractor.extract.assert_called_once()
        
        # Verify browser was closed
        browser_data["browser"].close.assert_called_once()
        
        # Verify result
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.logos, self.orchestrator.logo_extractor.extract.return_value)
        self.assertEqual(result.colors, self.orchestrator.color_extractor.extract.return_value["colors"])
        self.assertEqual(result.color_palette, self.orchestrator.color_extractor.extract.return_value["palette"])
        self.assertEqual(result.ui_style, self.orchestrator.ui_style_extractor.extract.return_value)
        self.assertEqual(result.screenshots, screenshots)
        self.assertEqual(result.metadata, browser_data["metadata"])
        
        # Verify result was cached
        cache_key = self.orchestrator._get_cache_key(request)
        self.assertIn(cache_key, self.orchestrator._cache)
        cached_timestamp, cached_result = self.orchestrator._cache[cache_key]
        self.assertEqual(cached_result, result)

    async def test_scrape_with_url_validation_error(self):
        """Test scraping with a URL validation error."""
        # Create a request
        request = ScrapingRequest(
            url="invalid-url",
            elements=["logos", "colors", "styles"],
        )
        
        # Mock validate_url to raise an error
        error_message = "Invalid URL format"
        self.orchestrator.validate_url.side_effect = ValueError(error_message)
        
        # Call scrape
        result = await self.orchestrator.scrape(request)
        
        # Verify validate_url was called
        self.orchestrator.validate_url.assert_called_once_with("invalid-url")
        
        # Verify result has an error
        self.assertEqual(result.url, "invalid-url")
        self.assertEqual(result.error, error_message)
        self.assertIsNone(result.logos)
        self.assertIsNone(result.colors)
        self.assertIsNone(result.ui_style)

    async def test_scrape_with_browser_error(self):
        """Test scraping with a browser error."""
        # Create a request
        request = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors", "styles"],
        )
        
        # Mock _setup_browser_and_navigate to return an error
        error_message = "Browser automation error"
        self.orchestrator._setup_browser_and_navigate = AsyncMock(return_value={"error": error_message})
        
        # Call scrape
        result = await self.orchestrator.scrape(request)
        
        # Verify validate_url was called
        self.orchestrator.validate_url.assert_called_once_with("https://example.com")
        
        # Verify _setup_browser_and_navigate was called
        self.orchestrator._setup_browser_and_navigate.assert_called_once()
        
        # Verify result has an error
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.error, error_message)
        self.assertIsNone(result.logos)
        self.assertIsNone(result.colors)
        self.assertIsNone(result.ui_style)

    async def test_scrape_with_comparison_urls(self):
        """Test scraping with comparison URLs."""
        # Create a request with comparison URLs
        request = ScrapingRequest(
            url="https://example.com",
            elements=["logos"],
            options={
                "comparison_urls": ["https://example.org", "https://example.net"],
            },
        )
        
        # Mock _setup_browser_and_navigate
        browser_data = {
            "browser": MagicMock(),
            "context": MagicMock(),
            "page": MagicMock(),
            "soup": MagicMock(),
        }
        self.orchestrator._setup_browser_and_navigate = AsyncMock(return_value=browser_data)
        
        # Mock _capture_screenshots
        screenshots = {"full": "base64_data"}
        self.orchestrator._capture_screenshots = AsyncMock(return_value=screenshots)
        
        # Mock extractors
        self.orchestrator.logo_extractor.extract = AsyncMock(return_value=[MagicMock()])
        
        # Mock _process_comparison_urls
        comparison_results = {
            "https://example.org": {"logos": [MagicMock()]},
            "https://example.net": {"logos": [MagicMock()]},
        }
        self.orchestrator._process_comparison_urls = AsyncMock(return_value=comparison_results)
        
        # Call scrape
        result = await self.orchestrator.scrape(request)
        
        # Verify _process_comparison_urls was called
        self.orchestrator._process_comparison_urls.assert_called_once_with(
            ["https://example.org", "https://example.net"],
            ["logos"],
            request.options,
        )
        
        # Verify result includes comparison results
        self.assertEqual(result.comparison_results, comparison_results)

    def test_get_cache_key(self):
        """Test generating cache keys."""
        # Create requests with different parameters
        request1 = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors"],
            selectors={"logo": ".logo"},
        )
        
        request2 = ScrapingRequest(
            url="https://example.com",
            elements=["colors", "logos"],  # Different order
            selectors={"logo": ".logo"},
        )
        
        request3 = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors"],
            selectors={"logo": ".different-logo"},  # Different selector
        )
        
        request4 = ScrapingRequest(
            url="https://example.org",  # Different URL
            elements=["logos", "colors"],
            selectors={"logo": ".logo"},
        )
        
        request5 = ScrapingRequest(
            url="https://example.com",
            elements=["logos", "colors"],
            selectors={"logo": ".logo"},
            options={"browser_type": "firefox"},  # With options
        )
        
        # Generate cache keys
        key1 = self.orchestrator._get_cache_key(request1)
        key2 = self.orchestrator._get_cache_key(request2)
        key3 = self.orchestrator._get_cache_key(request3)
        key4 = self.orchestrator._get_cache_key(request4)
        key5 = self.orchestrator._get_cache_key(request5)
        
        # Verify keys
        self.assertEqual(key1, key2)  # Element order shouldn't matter
        self.assertNotEqual(key1, key3)  # Different selectors should have different keys
        self.assertNotEqual(key1, key4)  # Different URLs should have different keys
        self.assertNotEqual(key1, key5)  # Different options should have different keys


if __name__ == "__main__":
    # Run tests
    unittest.main()