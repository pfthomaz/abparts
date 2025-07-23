"""Browser automation module for the Website Scraper MCP Server."""

import asyncio
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response

logger = logging.getLogger(__name__)


class BrowserAutomationEngine:
    """Browser automation engine for scraping websites."""

    def __init__(self) -> None:
        """Initialize the browser automation engine."""
        self.browser_type = "chromium"  # Default browser type
        self.viewport_size = {"width": 1280, "height": 800}  # Default viewport size
        self.timeout = 30000  # Default timeout in milliseconds
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 "
            "Website-Scraper-MCP/0.1.0"
        )

    async def setup_browser(
        self,
        browser_type: str = None,
        headless: bool = True,
        proxy: Optional[str] = None,
        viewport_size: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[Browser, BrowserContext]:
        """Set up browser and context with the specified options."""
        browser_type = browser_type or self.browser_type
        viewport_size = viewport_size or self.viewport_size
        user_agent = user_agent or self.user_agent
        timeout = timeout or self.timeout

        logger.info(f"Setting up {browser_type} browser (headless: {headless})")

        async with async_playwright() as p:
            # Select browser type
            if browser_type == "chromium":
                browser_instance = p.chromium
            elif browser_type == "firefox":
                browser_instance = p.firefox
            elif browser_type == "webkit":
                browser_instance = p.webkit
            else:
                logger.warning(f"Unknown browser type: {browser_type}, using chromium")
                browser_instance = p.chromium

            # Launch browser with appropriate options
            launch_options = {
                "headless": headless,
            }

            # Add proxy configuration if needed
            if proxy:
                launch_options["proxy"] = {"server": proxy}

            browser = await browser_instance.launch(**launch_options)

            # Create context with appropriate options
            context_options = {
                "viewport": viewport_size,
                "user_agent": user_agent,
                "bypass_csp": True,  # Bypass Content Security Policy
                "ignore_https_errors": True,  # Ignore HTTPS errors
            }

            context = await browser.new_context(**context_options)

            return browser, context

    async def navigate_to_url(
        self,
        context: BrowserContext,
        url: str,
        wait_until: str = "networkidle",
        timeout: Optional[int] = None,
        extra_http_headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Page, BeautifulSoup, Optional[str]]:
        """Navigate to URL and return page, soup, and error if any."""
        timeout = timeout or self.timeout
        page = await context.new_page()
        page.set_default_timeout(timeout)

        # Set extra HTTP headers if provided
        if extra_http_headers:
            await page.set_extra_http_headers(extra_http_headers)

        # Add event listeners for console messages and errors
        page.on("console", lambda msg: logger.debug(f"Console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: logger.warning(f"Page error: {err}"))

        # Navigate to URL
        logger.info(f"Navigating to {url}")
        try:
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout,
            )

            # Check response status
            if response is None:
                return page, None, "Failed to load page: No response received"

            if not response.ok:
                status = response.status
                return page, None, f"Failed to load page: HTTP status {status}"

            # Wait for page to be fully loaded
            await page.wait_for_load_state("networkidle")

            # Wait for any lazy-loaded content
            await asyncio.sleep(2)

            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            return page, soup, None

        except Exception as e:
            logger.exception(f"Error navigating to {url}: {e}")
            return page, None, f"Navigation error: {str(e)}"

    async def take_screenshot(
        self,
        page: Page,
        full_page: bool = True,
        element_selector: Optional[str] = None,
        path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Take a screenshot of the page or element."""
        try:
            if element_selector:
                element = await page.query_selector(element_selector)
                if element:
                    return await element.screenshot(path=path)
                else:
                    logger.warning(f"Element not found: {element_selector}")
                    return None
            else:
                return await page.screenshot(full_page=full_page, path=path)
        except Exception as e:
            logger.exception(f"Error taking screenshot: {e}")
            return None

    async def extract_element_styles(
        self, page: Page, selector: str
    ) -> Optional[Dict[str, Any]]:
        """Extract computed styles for an element."""
        try:
            element = await page.query_selector(selector)
            if not element:
                logger.warning(f"Element not found: {selector}")
                return None

            # Get computed styles
            styles = await page.evaluate(
                """(element) => {
                const style = window.getComputedStyle(element);
                const result = {};
                for (let i = 0; i < style.length; i++) {
                    const prop = style[i];
                    result[prop] = style.getPropertyValue(prop);
                }
                return result;
            }""",
                element,
            )

            return styles
        except Exception as e:
            logger.exception(f"Error extracting element styles: {e}")
            return None

    async def execute_javascript(self, page: Page, script: str) -> Any:
        """Execute JavaScript on the page."""
        try:
            return await page.evaluate(script)
        except Exception as e:
            logger.exception(f"Error executing JavaScript: {e}")
            return None

    async def wait_for_selector(
        self, page: Page, selector: str, timeout: Optional[int] = None
    ) -> bool:
        """Wait for an element matching the selector to appear."""
        timeout = timeout or self.timeout
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Timeout waiting for selector {selector}: {e}")
            return False

    async def scroll_page(self, page: Page, distance: Optional[int] = None) -> None:
        """Scroll the page by a specific distance or to the bottom."""
        try:
            if distance:
                await page.evaluate(f"window.scrollBy(0, {distance})")
            else:
                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception as e:
            logger.exception(f"Error scrolling page: {e}")

    async def get_page_metadata(self, page: Page) -> Dict[str, str]:
        """Extract metadata from the page."""
        try:
            metadata = await page.evaluate(
                """() => {
                const result = {};
                
                // Get meta tags
                const metaTags = document.querySelectorAll('meta');
                metaTags.forEach(meta => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    const content = meta.getAttribute('content');
                    if (name && content) {
                        result[name] = content;
                    }
                });
                
                // Get title
                result['title'] = document.title;
                
                // Get canonical URL
                const canonical = document.querySelector('link[rel="canonical"]');
                if (canonical) {
                    result['canonical'] = canonical.getAttribute('href');
                }
                
                return result;
            }"""
            )
            return metadata
        except Exception as e:
            logger.exception(f"Error getting page metadata: {e}")
            return {}