"""Tests for logo extraction functionality."""

import asyncio
import base64
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bs4 import BeautifulSoup
from website_scraper_mcp.extractors import LogoExtractor
from website_scraper_mcp.models import Logo


class TestLogoExtraction(unittest.TestCase):
    """Test the logo extraction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = LogoExtractor()

    @patch("website_scraper_mcp.extractors.LogoExtractor._find_logo_elements")
    @patch("website_scraper_mcp.extractors.LogoExtractor._process_logo_elements")
    async def test_extract_with_selector(self, mock_process, mock_find):
        """Test logo extraction with a provided selector."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        
        # Create a simple HTML with a logo
        html = """
        <html>
        <body>
            <div class="logo-container">
                <img src="/logo.png" alt="Example Logo" width="100" height="50">
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Set up the selector
        selector = ".logo-container img"
        
        # Mock process_logo_elements to return a logo
        mock_logo = Logo(
            url="https://example.com",
            src="https://example.com/logo.png",
            alt="Example Logo",
            width=100,
            height=50,
            format="png",
        )
        mock_process.return_value = [mock_logo]
        
        # Call extract method
        logos = await self.extractor.extract(mock_page, soup, selector)
        
        # Verify result
        self.assertEqual(len(logos), 1)
        self.assertEqual(logos[0].src, "https://example.com/logo.png")
        self.assertEqual(logos[0].alt, "Example Logo")
        
        # Verify that _find_logo_elements was not called (since selector was provided)
        mock_find.assert_not_called()
        
        # Verify that _process_logo_elements was called with the selected elements
        mock_process.assert_called_once()
        # Get the elements passed to _process_logo_elements
        elements = mock_process.call_args[0][1]
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].name, "img")
        self.assertEqual(elements[0]["src"], "/logo.png")

    @patch("website_scraper_mcp.extractors.LogoExtractor._find_logo_elements")
    @patch("website_scraper_mcp.extractors.LogoExtractor._process_logo_elements")
    @patch("website_scraper_mcp.extractors.LogoExtractor._try_additional_logo_strategies")
    @patch("website_scraper_mcp.extractors.LogoExtractor._score_and_rank_logos")
    async def test_extract_without_selector(self, mock_score, mock_additional, mock_process, mock_find):
        """Test logo extraction without a selector."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        
        # Mock find_logo_elements to return some elements
        mock_elements = [
            BeautifulSoup('<img src="/logo.png" alt="Logo">', "html.parser").img,
            BeautifulSoup('<svg width="100" height="50"></svg>', "html.parser").svg,
        ]
        mock_find.return_value = mock_elements
        
        # Mock process_logo_elements to return logos
        mock_logos = [
            Logo(
                url="https://example.com",
                src="https://example.com/logo.png",
                alt="Logo",
                format="png",
            ),
            Logo(
                url="https://example.com",
                src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjUwIj48L3N2Zz4=",
                alt="SVG Logo",
                format="svg",
            ),
        ]
        mock_process.return_value = mock_logos
        
        # Mock score_and_rank_logos to return the same logos
        mock_score.return_value = mock_logos
        
        # Call extract method
        logos = await self.extractor.extract(mock_page, soup)
        
        # Verify result
        self.assertEqual(len(logos), 2)
        self.assertEqual(logos[0].src, "https://example.com/logo.png")
        self.assertEqual(logos[1].format, "svg")
        
        # Verify method calls
        mock_find.assert_called_once_with(mock_page, soup)
        mock_process.assert_called_once_with(mock_page, mock_elements)
        mock_score.assert_called_once_with(mock_logos)
        mock_additional.assert_not_called()  # Should not be called since logos were found

    @patch("website_scraper_mcp.extractors.LogoExtractor._find_logo_elements")
    @patch("website_scraper_mcp.extractors.LogoExtractor._process_logo_elements")
    @patch("website_scraper_mcp.extractors.LogoExtractor._try_additional_logo_strategies")
    @patch("website_scraper_mcp.extractors.LogoExtractor._score_and_rank_logos")
    async def test_extract_with_additional_strategies(self, mock_score, mock_additional, mock_process, mock_find):
        """Test logo extraction with additional strategies when no logos found initially."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_page.url = "https://example.com"
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        
        # Mock find_logo_elements to return some elements
        mock_find.return_value = []
        
        # Mock process_logo_elements to return no logos
        mock_process.return_value = []
        
        # Mock additional strategies to return a logo
        mock_additional_logos = [
            Logo(
                url="https://example.com",
                src="https://example.com/favicon.ico",
                alt="Favicon",
                format="ico",
            ),
        ]
        mock_additional.return_value = mock_additional_logos
        
        # Mock score_and_rank_logos to return the same logos
        mock_score.return_value = mock_additional_logos
        
        # Call extract method
        logos = await self.extractor.extract(mock_page, soup)
        
        # Verify result
        self.assertEqual(len(logos), 1)
        self.assertEqual(logos[0].src, "https://example.com/favicon.ico")
        self.assertEqual(logos[0].alt, "Favicon")
        
        # Verify method calls
        mock_find.assert_called_once_with(mock_page, soup)
        mock_process.assert_called_once_with(mock_page, [])
        mock_additional.assert_called_once_with(mock_page, soup)
        mock_score.assert_called_once_with(mock_additional_logos)

    def test_score_and_rank_logos(self):
        """Test the logo scoring and ranking functionality."""
        # Create test logos
        logos = [
            Logo(
                url="https://example.com",
                src="https://example.com/icon.png",
                alt="Site Icon",
                format="png",
            ),
            Logo(
                url="https://example.com",
                src="https://example.com/logo.svg",
                alt="Company Logo",
                format="svg",
            ),
            Logo(
                url="https://example.com",
                src="https://example.com/header-image.jpg",
                alt="Header",
                format="jpg",
            ),
            Logo(
                url="https://example.com",
                src="https://example.com/brand-logo.png",
                alt="Brand",
                format="png",
            ),
            Logo(
                url="https://example.com",
                src="https://example.com/favicon.ico",
                alt="Favicon",
                format="ico",
            ),
        ]
        
        # Score and rank logos
        ranked_logos = self.extractor._score_and_rank_logos(logos)
        
        # Verify ranking
        self.assertEqual(len(ranked_logos), 5)
        
        # The logo.svg with "Company Logo" alt should be ranked highest
        self.assertEqual(ranked_logos[0].src, "https://example.com/logo.svg")
        self.assertEqual(ranked_logos[0].alt, "Company Logo")
        
        # The brand-logo.png should be ranked second
        self.assertEqual(ranked_logos[1].src, "https://example.com/brand-logo.png")
        
        # The favicon should be ranked lowest
        self.assertEqual(ranked_logos[-1].src, "https://example.com/favicon.ico")


if __name__ == "__main__":
    # Run tests
    unittest.main()