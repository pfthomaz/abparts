"""Tests for URL validation functionality."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.scraper import ScrapingOrchestrator


class TestURLValidation(unittest.TestCase):
    """Test the URL validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = ScrapingOrchestrator()

    @patch("website_scraper_mcp.scraper.aiohttp.ClientSession")
    async def test_valid_url(self, mock_session):
        """Test validation with a valid URL."""
        # Mock session response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.__aenter__.return_value = mock_response
        mock_response.text.return_value = ""
        
        mock_session_instance = MagicMock()
        mock_session_instance.head.return_value = mock_response
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.__aenter__.return_value = mock_session_instance
        
        mock_session.return_value = mock_session_instance
        
        # Test validation
        try:
            await self.orchestrator.validate_url("https://example.com")
            # If we get here, validation passed
            self.assertTrue(True)
        except ValueError:
            self.fail("validate_url() raised ValueError unexpectedly!")

    async def test_invalid_url_format(self):
        """Test validation with invalid URL format."""
        invalid_urls = [
            "example.com",  # Missing scheme
            "ftp://example.com",  # Invalid scheme
            "http://",  # Missing netloc
            "",  # Empty string
            "http:example.com",  # Malformed URL
        ]
        
        for url in invalid_urls:
            with self.assertRaises(ValueError):
                await self.orchestrator.validate_url(url)

    @patch("website_scraper_mcp.scraper.aiohttp.ClientSession")
    async def test_unreachable_url(self, mock_session):
        """Test validation with unreachable URL."""
        # Mock session response for unreachable URL
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.__aenter__.return_value = mock_response
        
        mock_session_instance = MagicMock()
        mock_session_instance.head.return_value = mock_response
        mock_session_instance.__aenter__.return_value = mock_session_instance
        
        mock_session.return_value = mock_session_instance
        
        # Test validation
        with self.assertRaises(ValueError) as context:
            await self.orchestrator.validate_url("https://example.com/not-found")
        
        self.assertIn("status code 404", str(context.exception))

    @patch("website_scraper_mcp.scraper.aiohttp.ClientSession")
    async def test_robots_txt_blocked(self, mock_session):
        """Test validation with URL blocked by robots.txt."""
        # Mock session response for head request
        mock_head_response = AsyncMock()
        mock_head_response.status = 200
        mock_head_response.__aenter__.return_value = mock_head_response
        
        # Mock session response for robots.txt
        mock_robots_response = AsyncMock()
        mock_robots_response.status = 200
        mock_robots_response.__aenter__.return_value = mock_robots_response
        mock_robots_response.text.return_value = """
        User-agent: *
        Disallow: /private/
        """
        
        mock_session_instance = MagicMock()
        mock_session_instance.head.return_value = mock_head_response
        mock_session_instance.get.return_value = mock_robots_response
        mock_session_instance.__aenter__.return_value = mock_session_instance
        
        mock_session.return_value = mock_session_instance
        
        # Test validation
        with self.assertRaises(ValueError) as context:
            await self.orchestrator.validate_url("https://example.com/private/page")
        
        self.assertIn("robots.txt", str(context.exception))

    def test_is_url_blocked_by_robots(self):
        """Test the _is_url_blocked_by_robots method."""
        # Test with URL that should be blocked
        robots_txt = """
        User-agent: *
        Disallow: /private/
        
        User-agent: website-scraper-mcp
        Disallow: /api/
        """
        
        # Should be blocked by * rule
        self.assertTrue(
            self.orchestrator._is_url_blocked_by_robots(
                robots_txt, "https://example.com/private/page"
            )
        )
        
        # Should be blocked by specific agent rule
        self.assertTrue(
            self.orchestrator._is_url_blocked_by_robots(
                robots_txt, "https://example.com/api/data"
            )
        )
        
        # Should not be blocked
        self.assertFalse(
            self.orchestrator._is_url_blocked_by_robots(
                robots_txt, "https://example.com/public/page"
            )
        )
        
        # Test with Allow directive
        robots_txt = """
        User-agent: *
        Disallow: /private/
        Allow: /private/public
        """
        
        # Should be blocked
        self.assertTrue(
            self.orchestrator._is_url_blocked_by_robots(
                robots_txt, "https://example.com/private/secret"
            )
        )
        
        # Should not be blocked due to Allow directive
        self.assertFalse(
            self.orchestrator._is_url_blocked_by_robots(
                robots_txt, "https://example.com/private/public/page"
            )
        )


if __name__ == "__main__":
    # Run tests
    unittest.main()