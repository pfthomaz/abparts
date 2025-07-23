"""Scraping orchestrator for the Website Scraper MCP Server."""

import asyncio
import base64
import logging
import re
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from website_scraper_mcp.browser_automation import BrowserAutomationEngine
from website_scraper_mcp.extractors import (
    ColorExtractor,
    LogoExtractor,
    UIStyleExtractor,
)
from website_scraper_mcp.models import ScrapingRequest, ScrapingResult

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """Orchestrates the website scraping process."""

    def __init__(self) -> None:
        """Initialize the scraping orchestrator."""
        self.logo_extractor = LogoExtractor()
        self.color_extractor = ColorExtractor()
        self.ui_style_extractor = UIStyleExtractor()
        self.browser_engine = BrowserAutomationEngine()
        self._cache: Dict[str, Tuple[datetime, ScrapingResult]] = {}
        self._cache_ttl = 3600  # 1 hour

    async def scrape(self, request: ScrapingRequest) -> ScrapingResult:
        """Orchestrate the scraping process for the given URL."""
        # Process options
        options = request.options or {}
        cache_ttl = options.get("cache_ttl", self._cache_ttl)
        
        # Check cache
        cache_key = self._get_cache_key(request)
        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < cache_ttl:
                logger.info(f"Using cached result for {request.url}")
                return result

        # Validate URL
        try:
            await self.validate_url(request.url)
        except ValueError as e:
            logger.error(f"URL validation failed: {e}")
            return ScrapingResult(url=request.url, error=str(e))

        # Initialize result
        result = ScrapingResult(url=request.url)

        try:
            # Set up browser options
            browser_options = {
                "browser_type": options.get("browser_type", "chromium"),
                "headless": True,
                "proxy": options.get("proxy"),
                "viewport_size": {
                    "width": options.get("viewport_width", 1280),
                    "height": options.get("viewport_height", 800),
                },
                "user_agent": options.get("user_agent"),
                "timeout": options.get("timeout", 30000),
            }
            
            # Launch browser and navigate to page
            browser_data = await self._setup_browser_and_navigate(
                request.url,
                browser_options=browser_options,
                wait_until=options.get("wait_until", "networkidle"),
            )
            
            if browser_data.get("error"):
                return ScrapingResult(url=request.url, error=browser_data["error"])
            
            page = browser_data["page"]
            browser = browser_data["browser"]
            context = browser_data["context"]
            soup = browser_data["soup"]
            
            # Add metadata to result
            if browser_data.get("metadata"):
                result.metadata = browser_data["metadata"]
            
            # Take screenshots
            screenshots = await self._capture_screenshots(page)
            result.screenshots = screenshots
            
            # Extract requested elements
            if "logos" in request.elements:
                logger.info("Extracting logos")
                logo_selector = request.selectors.get("logo") if request.selectors else None
                result.logos = await self.logo_extractor.extract(page, soup, logo_selector)

            if "colors" in request.elements:
                logger.info("Extracting colors")
                color_options = {
                    "element_focus": options.get("element_focus"),
                    "include_images": options.get("include_images", True),
                }
                colors_result = await self.color_extractor.extract(
                    page, soup, base64.b64decode(screenshots["full"]), color_options
                )
                result.colors = colors_result.get("colors")
                result.color_palette = colors_result.get("palette")

            if "styles" in request.elements:
                logger.info("Extracting UI styles")
                style_options = {
                    "component_types": options.get("component_types", []),
                }
                result.ui_style = await self.ui_style_extractor.extract(page, soup, style_options)

            # Handle comparison URLs if provided
            comparison_urls = options.get("comparison_urls", [])
            if comparison_urls:
                logger.info(f"Processing {len(comparison_urls)} comparison URLs")
                result.comparison_results = await self._process_comparison_urls(
                    comparison_urls, request.elements, options
                )

            # Close browser
            await browser.close()

            # Cache result
            self._cache[cache_key] = (datetime.now(), result)
            return result

        except Exception as e:
            logger.exception(f"Error during scraping: {e}")
            return ScrapingResult(url=request.url, error=str(e))
            
    async def _setup_browser_and_navigate(
        self, url: str, browser_options: Dict[str, Any] = None, wait_until: str = "networkidle"
    ) -> Dict[str, Any]:
        """Set up browser and navigate to URL."""
        logger.info(f"Setting up browser and navigating to {url}")
        browser_options = browser_options or {}
        
        try:
            # Set up browser and context
            browser, context = await self.browser_engine.setup_browser(
                browser_type=browser_options.get("browser_type"),
                headless=browser_options.get("headless", True),
                proxy=browser_options.get("proxy"),
                viewport_size=browser_options.get("viewport_size"),
                user_agent=browser_options.get("user_agent"),
                timeout=browser_options.get("timeout"),
            )
            
            # Set up extra HTTP headers if provided
            extra_headers = browser_options.get("extra_headers")
            
            # Navigate to URL
            page, soup, error = await self.browser_engine.navigate_to_url(
                context, 
                url, 
                wait_until=wait_until,
                timeout=browser_options.get("timeout"),
                extra_http_headers=extra_headers,
            )
            
            if error:
                await browser.close()
                return {"error": error}
            
            # Get page metadata
            metadata = await self.browser_engine.get_page_metadata(page)
            logger.info(f"Page title: {metadata.get('title', 'Unknown')}")
            
            return {
                "browser": browser,
                "context": context,
                "page": page,
                "soup": soup,
                "metadata": metadata,
            }
                
        except Exception as e:
            logger.exception(f"Error setting up browser: {e}")
            return {"error": f"Browser automation error: {str(e)}"}
            
    async def _capture_screenshots(self, page) -> Dict[str, str]:
        """Capture screenshots of the page."""
        logger.info("Capturing screenshots")
        screenshots = {}
        
        try:
            # Full page screenshot
            full_screenshot = await self.browser_engine.take_screenshot(page, full_page=True)
            if full_screenshot:
                screenshots["full"] = base64.b64encode(full_screenshot).decode("utf-8")
            
            # Above the fold screenshot (viewport only)
            viewport_screenshot = await self.browser_engine.take_screenshot(page, full_page=False)
            if viewport_screenshot:
                screenshots["viewport"] = base64.b64encode(viewport_screenshot).decode("utf-8")
            
            # Try to capture specific elements
            element_selectors = {
                "header": "header, nav, .header, #header",
                "main": "main, .main, #main, article, .content, #content",
                "footer": "footer, .footer, #footer",
                "logo": ".logo, #logo, [class*='logo'], [id*='logo'], header img",
            }
            
            for name, selector in element_selectors.items():
                screenshot = await self.browser_engine.take_screenshot(page, element_selector=selector)
                if screenshot:
                    screenshots[name] = base64.b64encode(screenshot).decode("utf-8")
            
            return screenshots
            
        except Exception as e:
            logger.warning(f"Error capturing screenshots: {e}")
            return {"error": str(e)}

    async def _process_comparison_urls(
        self, urls: List[str], elements: List[str], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process comparison URLs."""
        results = {}
        
        for url in urls:
            try:
                # Create a new request for the comparison URL
                comparison_request = ScrapingRequest(
                    url=url,
                    elements=elements,
                    options=options,
                )
                
                # Scrape the comparison URL
                logger.info(f"Scraping comparison URL: {url}")
                comparison_result = await self.scrape(comparison_request)
                
                # Add to results
                results[url] = {
                    "logos": comparison_result.logos,
                    "colors": comparison_result.colors,
                    "color_palette": comparison_result.color_palette,
                    "ui_style": comparison_result.ui_style,
                    "metadata": comparison_result.metadata,
                }
                
            except Exception as e:
                logger.warning(f"Error processing comparison URL {url}: {e}")
                results[url] = {"error": str(e)}
        
        return results

    async def validate_url(self, url: str) -> None:
        """Validate URL and check robots.txt compliance."""
        logger.info(f"Validating URL: {url}")
        
        # Check URL format
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                logger.error(f"Invalid URL format: {url}")
                raise ValueError("Invalid URL format. URL must include scheme (http:// or https://) and domain.")
            
            # Ensure scheme is http or https
            if parsed.scheme not in ["http", "https"]:
                logger.error(f"Invalid URL scheme: {parsed.scheme}")
                raise ValueError("URL scheme must be http or https.")
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            raise ValueError(f"Invalid URL format: {e}")

        # Check if URL is reachable
        try:
            headers = {
                "User-Agent": "Website-Scraper-MCP/0.1.0 (+https://github.com/your-repo/website-scraper-mcp)"
            }
            async with aiohttp.ClientSession() as session:
                async with session.head(url, allow_redirects=True, timeout=10, headers=headers) as response:
                    if response.status >= 400:
                        logger.error(f"URL returned status code {response.status}: {url}")
                        raise ValueError(f"URL returned status code {response.status}. The website may be unavailable or blocking requests.")
        except aiohttp.ClientError as e:
            logger.error(f"Connection error for URL {url}: {e}")
            raise ValueError(f"Could not connect to URL: {e}. Please check the URL and your internet connection.")
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout for URL {url}")
            raise ValueError("Connection timed out. The website may be slow or unavailable.")

        # Check robots.txt
        await self._check_robots_txt(parsed, url)

    async def _check_robots_txt(self, parsed_url, original_url: str) -> None:
        """Check if URL is allowed by robots.txt."""
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        logger.info(f"Checking robots.txt at: {robots_url}")
        
        try:
            headers = {
                "User-Agent": "Website-Scraper-MCP/0.1.0 (+https://github.com/your-repo/website-scraper-mcp)"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5, headers=headers) as response:
                    if response.status == 200:
                        robots_txt = await response.text()
                        if self._is_url_blocked_by_robots(robots_txt, original_url):
                            logger.warning(f"URL is blocked by robots.txt: {original_url}")
                            raise ValueError(
                                "This URL is blocked by the website's robots.txt file. "
                                "Scraping this URL would violate the website's terms of service."
                            )
                        else:
                            logger.info(f"URL is allowed by robots.txt: {original_url}")
                    else:
                        logger.info(f"No robots.txt found or accessible (status {response.status})")
        except aiohttp.ClientError as e:
            # If robots.txt doesn't exist or can't be fetched, log and continue
            logger.info(f"Could not fetch robots.txt ({e}), assuming scraping is allowed")
        except asyncio.TimeoutError:
            logger.info("Timeout while fetching robots.txt, assuming scraping is allowed")

    def _is_url_blocked_by_robots(self, robots_txt: str, url: str) -> bool:
        """Check if URL is blocked by robots.txt."""
        parsed = urlparse(url)
        path = parsed.path or "/"

        # Simple robots.txt parser
        user_agent = None
        current_rules_apply = False
        
        for line in robots_txt.split("\n"):
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue

            if line.startswith("user-agent:"):
                agent = line[11:].strip()
                # Check if this rule applies to us
                # Order of precedence: website-scraper-mcp, * (all agents)
                if agent == "website-scraper-mcp":
                    user_agent = agent
                    current_rules_apply = True
                elif agent == "*" and user_agent != "website-scraper-mcp":
                    user_agent = agent
                    current_rules_apply = True
                else:
                    current_rules_apply = False
            
            elif current_rules_apply and line.startswith("disallow:"):
                disallow_path = line[9:].strip()
                if disallow_path and path.startswith(disallow_path):
                    return True
            
            elif current_rules_apply and line.startswith("allow:"):
                allow_path = line[6:].strip()
                # If there's an explicit allow that matches our path, it overrides any disallow
                if allow_path and path.startswith(allow_path):
                    return False

        return False

    def _get_cache_key(self, request: ScrapingRequest) -> str:
        """Generate a cache key for the request."""
        elements = ",".join(sorted(request.elements))
        selectors = ",".join(f"{k}:{v}" for k, v in sorted(request.selectors.items())) if request.selectors else ""
        
        # Include relevant options in the cache key
        options_dict = request.options or {}
        relevant_options = [
            "element_focus",
            "component_types",
            "browser_type",
            "viewport_width",
            "viewport_height",
        ]
        options_str = ",".join(
            f"{k}:{options_dict.get(k)}" 
            for k in relevant_options 
            if k in options_dict
        )
        
        return f"{request.url}|{elements}|{selectors}|{options_str}"