"""Tests for the browser automation module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.browser_automation import BrowserAutomationEngine


class TestBrowserAutomationEngine(unittest.TestCase):
    """Test the BrowserAutomationEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = BrowserAutomationEngine()

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_setup_browser_default_options(self, mock_playwright):
        """Test setting up browser with default options."""
        # Mock playwright
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser_instance = AsyncMock()
        mock_browser_instance.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__aenter__.return_value.chromium = mock_browser_instance
        
        # Call setup_browser
        browser, context = await self.engine.setup_browser()
        
        # Verify browser was launched with correct options
        mock_browser_instance.launch.assert_called_once_with(headless=True)
        
        # Verify context was created with correct options
        mock_browser.new_context.assert_called_once()
        context_options = mock_browser.new_context.call_args[1]
        self.assertEqual(context_options["viewport"], {"width": 1280, "height": 800})
        self.assertTrue("user_agent" in context_options)
        self.assertTrue(context_options["bypass_csp"])
        self.assertTrue(context_options["ignore_https_errors"])
        
        # Verify return values
        self.assertEqual(browser, mock_browser)
        self.assertEqual(context, mock_context)

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_setup_browser_custom_options(self, mock_playwright):
        """Test setting up browser with custom options."""
        # Mock playwright
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser_instance = AsyncMock()
        mock_browser_instance.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__aenter__.return_value.firefox = mock_browser_instance
        
        # Custom options
        browser_type = "firefox"
        headless = False
        proxy = "http://proxy.example.com:8080"
        viewport_size = {"width": 1920, "height": 1080}
        user_agent = "Custom User Agent"
        timeout = 60000
        
        # Call setup_browser with custom options
        browser, context = await self.engine.setup_browser(
            browser_type=browser_type,
            headless=headless,
            proxy=proxy,
            viewport_size=viewport_size,
            user_agent=user_agent,
            timeout=timeout,
        )
        
        # Verify browser was launched with correct options
        mock_browser_instance.launch.assert_called_once_with(
            headless=headless,
            proxy={"server": proxy},
        )
        
        # Verify context was created with correct options
        mock_browser.new_context.assert_called_once()
        context_options = mock_browser.new_context.call_args[1]
        self.assertEqual(context_options["viewport"], viewport_size)
        self.assertEqual(context_options["user_agent"], user_agent)
        self.assertTrue(context_options["bypass_csp"])
        self.assertTrue(context_options["ignore_https_errors"])
        
        # Verify return values
        self.assertEqual(browser, mock_browser)
        self.assertEqual(context, mock_context)

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_navigate_to_url_success(self, mock_playwright):
        """Test navigating to URL successfully."""
        # Mock context and page
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        mock_context.new_page.return_value = mock_page
        
        # Mock page methods
        mock_page.goto.return_value = mock_response
        mock_response.ok = True
        mock_page.content.return_value = "<html><body>Test</body></html>"
        
        # Call navigate_to_url
        page, soup, error = await self.engine.navigate_to_url(mock_context, "https://example.com")
        
        # Verify page was created and navigated
        mock_context.new_page.assert_called_once()
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="networkidle",
            timeout=30000,
        )
        
        # Verify return values
        self.assertEqual(page, mock_page)
        self.assertIsNotNone(soup)
        self.assertEqual(soup.body.text, "Test")
        self.assertIsNone(error)

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_navigate_to_url_error(self, mock_playwright):
        """Test navigating to URL with error."""
        # Mock context and page
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        mock_context.new_page.return_value = mock_page
        
        # Mock page methods with error response
        mock_page.goto.return_value = mock_response
        mock_response.ok = False
        mock_response.status = 404
        
        # Call navigate_to_url
        page, soup, error = await self.engine.navigate_to_url(mock_context, "https://example.com/notfound")
        
        # Verify page was created and navigated
        mock_context.new_page.assert_called_once()
        mock_page.goto.assert_called_once()
        
        # Verify return values
        self.assertEqual(page, mock_page)
        self.assertIsNone(soup)
        self.assertIsNotNone(error)
        self.assertIn("404", error)

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_take_screenshot(self, mock_playwright):
        """Test taking screenshots."""
        # Mock page
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        
        # Mock screenshot methods
        mock_page.screenshot.return_value = b"page_screenshot_data"
        mock_element.screenshot.return_value = b"element_screenshot_data"
        mock_page.query_selector.return_value = mock_element
        
        # Test full page screenshot
        screenshot_data = await self.engine.take_screenshot(mock_page, full_page=True)
        mock_page.screenshot.assert_called_with(full_page=True, path=None)
        self.assertEqual(screenshot_data, b"page_screenshot_data")
        
        # Test element screenshot
        screenshot_data = await self.engine.take_screenshot(mock_page, element_selector=".logo")
        mock_page.query_selector.assert_called_with(".logo")
        mock_element.screenshot.assert_called_with(path=None)
        self.assertEqual(screenshot_data, b"element_screenshot_data")

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_extract_element_styles(self, mock_playwright):
        """Test extracting element styles."""
        # Mock page and element
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        
        # Mock evaluate method
        mock_page.query_selector.return_value = mock_element
        mock_page.evaluate.return_value = {
            "color": "#000000",
            "backgroundColor": "#ffffff",
            "fontSize": "16px",
        }
        
        # Test extract_element_styles
        styles = await self.engine.extract_element_styles(mock_page, ".button")
        
        # Verify selector was used
        mock_page.query_selector.assert_called_with(".button")
        
        # Verify evaluate was called
        mock_page.evaluate.assert_called_once()
        
        # Verify return value
        self.assertEqual(styles["color"], "#000000")
        self.assertEqual(styles["backgroundColor"], "#ffffff")
        self.assertEqual(styles["fontSize"], "16px")

    @patch("website_scraper_mcp.browser_automation.async_playwright")
    async def test_get_page_metadata(self, mock_playwright):
        """Test getting page metadata."""
        # Mock page
        mock_page = AsyncMock()
        
        # Mock evaluate method
        mock_page.evaluate.return_value = {
            "title": "Test Page",
            "og:description": "Test description",
            "canonical": "https://example.com/canonical",
        }
        
        # Test get_page_metadata
        metadata = await self.engine.get_page_metadata(mock_page)
        
        # Verify evaluate was called
        mock_page.evaluate.assert_called_once()
        
        # Verify return value
        self.assertEqual(metadata["title"], "Test Page")
        self.assertEqual(metadata["og:description"], "Test description")
        self.assertEqual(metadata["canonical"], "https://example.com/canonical")


if __name__ == "__main__":
    # Run tests
    unittest.main()