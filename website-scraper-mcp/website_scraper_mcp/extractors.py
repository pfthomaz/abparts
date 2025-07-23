"""Extractors for the Website Scraper MCP Server."""

import base64
import io
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import colorthief
from bs4 import BeautifulSoup, Tag
from PIL import Image
from playwright.async_api import Page

from website_scraper_mcp.image_processor import ImageProcessor
from website_scraper_mcp.models import Color, ComponentStyle, Logo, Typography, UIStyle

logger = logging.getLogger(__name__)


class LogoExtractor:
    """Extracts logos from websites."""
    
    def __init__(self):
        """Initialize the logo extractor."""
        self.image_processor = ImageProcessor()

    async def extract(
        self, page: Page, soup: BeautifulSoup, selector: Optional[str] = None
    ) -> List[Logo]:
        """Extract logos from the page."""
        logos = []

        try:
            # Use selector if provided
            if selector:
                logger.info(f"Using provided selector for logo: {selector}")
                elements = soup.select(selector)
                if not elements:
                    logger.warning(f"No elements found with selector: {selector}")
            else:
                # Use multiple detection strategies
                elements = await self._find_logo_elements(page, soup)
            
            # Process found elements
            logos = await self._process_logo_elements(page, elements)
            
            # If no logos found, try additional strategies
            if not logos:
                logger.info("No logos found with primary strategy, trying additional methods")
                logos = await self._try_additional_logo_strategies(page, soup)
            
            # Score and rank logos
            if logos:
                logos = self._score_and_rank_logos(logos)
                logger.info(f"Found {len(logos)} potential logos")
            else:
                logger.warning("No logos found")
            
            return logos

        except Exception as e:
            logger.exception(f"Error extracting logos: {e}")
            return []
            
    async def _find_logo_elements(self, page: Page, soup: BeautifulSoup) -> List[Tag]:
        """Find potential logo elements using multiple strategies."""
        elements = []
        
        # Strategy 1: Common logo selectors
        logger.info("Finding logo elements using common selectors")
        common_selectors = [
            # Direct logo indicators
            "img[src*=logo]",
            "img[alt*=logo]",
            "img[title*=logo]",
            "svg[class*=logo]",
            "svg[id*=logo]",
            ".logo img",
            "#logo img",
            ".logo svg",
            "#logo svg",
            ".logo",
            "#logo",
            
            # Common logo containers
            "a[class*=logo] img",
            "a[id*=logo] img",
            "div[class*=logo] img",
            "div[id*=logo] img",
            "h1 img",  # Often logos are in h1 tags
            "header img:first-of-type",  # First image in header is often a logo
            ".header img:first-of-type",
            "#header img:first-of-type",
            ".navbar-brand img",  # Bootstrap navbar brand
            ".brand img",
            "#brand img",
            
            # Common logo patterns
            "[class*=logo]",
            "[id*=logo]",
            "[class*=brand] img",
            "[id*=brand] img",
            "a[href='/'] img",  # Logo often links to homepage
        ]
        
        for selector in common_selectors:
            elements.extend(soup.select(selector))
        
        # Strategy 2: Position-based heuristics (top-left elements)
        logger.info("Finding logo elements using position-based heuristics")
        top_left_elements = await self._find_top_left_elements(page)
        elements.extend(top_left_elements)
        
        # Strategy 3: Size-based heuristics
        logger.info("Finding logo elements using size-based heuristics")
        size_based_elements = await self._find_size_based_elements(page)
        elements.extend(size_based_elements)
        
        # Remove duplicates while preserving order
        unique_elements = []
        seen_elements = set()
        for element in elements:
            element_str = str(element)
            if element_str not in seen_elements:
                seen_elements.add(element_str)
                unique_elements.append(element)
        
        return unique_elements
    
    async def _find_top_left_elements(self, page: Page) -> List[Tag]:
        """Find elements in the top-left corner of the page."""
        elements_html = await page.evaluate("""() => {
            const elements = [];
            
            // Get all images and SVGs in the top 20% of the page
            const pageHeight = window.innerHeight;
            const pageWidth = window.innerWidth;
            const topThreshold = pageHeight * 0.2;
            const leftThreshold = pageWidth * 0.3;
            
            // Check images
            document.querySelectorAll('img').forEach(img => {
                const rect = img.getBoundingClientRect();
                if (rect.top < topThreshold && rect.left < leftThreshold && 
                    rect.width > 20 && rect.height > 20 && 
                    rect.width < pageWidth * 0.5 && rect.height < pageHeight * 0.3) {
                    elements.push(img.outerHTML);
                }
            });
            
            // Check SVGs
            document.querySelectorAll('svg').forEach(svg => {
                const rect = svg.getBoundingClientRect();
                if (rect.top < topThreshold && rect.left < leftThreshold && 
                    rect.width > 20 && rect.height > 20 && 
                    rect.width < pageWidth * 0.5 && rect.height < pageHeight * 0.3) {
                    elements.push(svg.outerHTML);
                }
            });
            
            return elements;
        }""")
        
        # Convert HTML strings back to BeautifulSoup elements
        elements = []
        for html in elements_html:
            element = BeautifulSoup(html, "html.parser")
            if element.contents:
                elements.append(element.contents[0])
        
        return elements
    
    async def _find_size_based_elements(self, page: Page) -> List[Tag]:
        """Find elements with typical logo dimensions."""
        elements_html = await page.evaluate("""() => {
            const elements = [];
            
            // Get all images with reasonable logo dimensions
            document.querySelectorAll('img').forEach(img => {
                const rect = img.getBoundingClientRect();
                
                // Typical logo aspect ratios are between 0.5 and 3.0
                const aspectRatio = rect.width / rect.height;
                
                if (rect.width >= 30 && rect.width <= 300 && 
                    rect.height >= 30 && rect.height <= 150 && 
                    aspectRatio >= 0.5 && aspectRatio <= 3.0) {
                    elements.push(img.outerHTML);
                }
            });
            
            // Check SVGs with similar criteria
            document.querySelectorAll('svg').forEach(svg => {
                const rect = svg.getBoundingClientRect();
                const aspectRatio = rect.width / rect.height;
                
                if (rect.width >= 30 && rect.width <= 300 && 
                    rect.height >= 30 && rect.height <= 150 && 
                    aspectRatio >= 0.5 && aspectRatio <= 3.0) {
                    elements.push(svg.outerHTML);
                }
            });
            
            return elements;
        }""")
        
        # Convert HTML strings back to BeautifulSoup elements
        elements = []
        for html in elements_html:
            element = BeautifulSoup(html, "html.parser")
            if element.contents:
                elements.append(element.contents[0])
        
        return elements
    
    async def _process_logo_elements(self, page: Page, elements: List[Tag]) -> List[Logo]:
        """Process found elements into Logo objects."""
        logos = []
        base_url = f"{page.url.split('/', 3)[0]}//{page.url.split('/', 3)[2]}"
        
        for element in elements:
            try:
                if element.name == "img":
                    src = element.get("src", "")
                    if not src:
                        continue
                    
                    # Make relative URLs absolute
                    if src.startswith("data:"):
                        # Data URL, keep as is
                        pass
                    elif src.startswith("//"):
                        # Protocol-relative URL
                        src = f"https:{src}"
                    elif src.startswith("/"):
                        # Root-relative URL
                        src = f"{base_url}{src}"
                    elif not src.startswith(("http://", "https://")):
                        # Path-relative URL
                        path_base = "/".join(page.url.split("/")[:-1])
                        src = f"{path_base}/{src}"
                    
                    # Get image format
                    if src.startswith("data:image/"):
                        format = src.split(";")[0].split("/")[1]
                    else:
                        format = src.split(".")[-1].lower() if "." in src else "unknown"
                        if format not in ["jpg", "jpeg", "png", "gif", "svg", "webp", "ico"]:
                            format = "unknown"
                    
                    # Get dimensions
                    width = element.get("width")
                    height = element.get("height")
                    
                    if width and width.isdigit():
                        width = int(width)
                    else:
                        width = None
                        
                    if height and height.isdigit():
                        height = int(height)
                    else:
                        height = None
                    
                    # Create logo object
                    logo = Logo(
                        url=page.url,
                        src=src,
                        alt=element.get("alt", ""),
                        width=width,
                        height=height,
                        format=format,
                    )
                    logos.append(logo)
                
                elif element.name == "svg":
                    # Extract SVG content
                    svg_content = str(element)
                    
                    # Try to get dimensions
                    width = element.get("width")
                    height = element.get("height")
                    
                    if width and width.isdigit():
                        width = int(width)
                    else:
                        width = None
                        
                    if height and height.isdigit():
                        height = int(height)
                    else:
                        height = None
                    
                    # Create logo object
                    logo = Logo(
                        url=page.url,
                        src="data:image/svg+xml;base64," + base64.b64encode(svg_content.encode()).decode(),
                        alt="SVG Logo",
                        width=width,
                        height=height,
                        format="svg",
                        data=svg_content,
                    )
                    logos.append(logo)
            
            except Exception as e:
                logger.warning(f"Error processing logo element: {e}")
        
        # Process logo images
        processed_logos = []
        for logo in logos:
            try:
                # Process image
                processed_logo = await self._process_logo_image(logo)
                processed_logos.append(processed_logo)
            except Exception as e:
                logger.warning(f"Error processing logo image: {e}")
                processed_logos.append(logo)  # Add original logo as fallback
        
        return processed_logos
        
    async def _process_logo_image(self, logo: Logo) -> Logo:
        """Process a logo image to extract additional information."""
        # Skip processing for logos with data already set
        if logo.data:
            return logo
        
        # Process image
        image_info = await self.image_processor.fetch_and_process_image(logo.src)
        
        # Update logo with processed image data
        if image_info["data"]:
            logo.data = image_info["data"]
        
        # Update dimensions if not already set
        if logo.width is None and image_info["width"]:
            logo.width = image_info["width"]
        
        if logo.height is None and image_info["height"]:
            logo.height = image_info["height"]
        
        # Update format if it was unknown
        if logo.format == "unknown" and image_info["format"]:
            logo.format = image_info["format"]
        
        return logo
    
    async def _try_additional_logo_strategies(self, page: Page, soup: BeautifulSoup) -> List[Logo]:
        """Try additional strategies to find logos."""
        logos = []
        
        # Strategy 1: Look for favicon
        logger.info("Looking for favicon")
        favicon = soup.find("link", rel=lambda r: r and ("icon" in r.lower() or "shortcut" in r.lower()))
        if favicon and favicon.get("href"):
            href = favicon.get("href")
            
            # Make relative URLs absolute
            base_url = f"{page.url.split('/', 3)[0]}//{page.url.split('/', 3)[2]}"
            if href.startswith("//"):
                href = f"https:{href}"
            elif href.startswith("/"):
                href = f"{base_url}{href}"
            elif not href.startswith(("http://", "https://")):
                path_base = "/".join(page.url.split("/")[:-1])
                href = f"{path_base}/{href}"
            
            # Get format
            format = href.split(".")[-1].lower() if "." in href else "ico"
            if format not in ["ico", "png", "jpg", "jpeg", "gif", "svg"]:
                format = "ico"
            
            # Create logo object
            logo = Logo(
                url=page.url,
                src=href,
                alt="Favicon",
                width=None,
                height=None,
                format=format,
            )
            logos.append(logo)
        
        # Strategy 2: Look for Open Graph image
        logger.info("Looking for Open Graph image")
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            content = og_image.get("content")
            
            # Make relative URLs absolute
            base_url = f"{page.url.split('/', 3)[0]}//{page.url.split('/', 3)[2]}"
            if content.startswith("//"):
                content = f"https:{content}"
            elif content.startswith("/"):
                content = f"{base_url}{content}"
            elif not content.startswith(("http://", "https://")):
                path_base = "/".join(page.url.split("/")[:-1])
                content = f"{path_base}/{content}"
            
            # Get format
            format = content.split(".")[-1].lower() if "." in content else "unknown"
            if format not in ["jpg", "jpeg", "png", "gif", "svg", "webp"]:
                format = "unknown"
            
            # Create logo object
            logo = Logo(
                url=page.url,
                src=content,
                alt="Open Graph Image",
                width=None,
                height=None,
                format=format,
            )
            logos.append(logo)
        
        # Strategy 3: Look for schema.org logo
        logger.info("Looking for schema.org logo")
        schema_scripts = soup.find_all("script", type="application/ld+json")
        for script in schema_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    logo_url = None
                    
                    # Check for logo in Organization
                    if isinstance(data, dict):
                        if data.get("@type") == "Organization" and data.get("logo"):
                            logo_url = data.get("logo")
                        elif data.get("publisher") and data.get("publisher").get("logo"):
                            logo_url = data.get("publisher").get("logo").get("url")
                    
                    if logo_url:
                        # Make relative URLs absolute
                        base_url = f"{page.url.split('/', 3)[0]}//{page.url.split('/', 3)[2]}"
                        if logo_url.startswith("//"):
                            logo_url = f"https:{logo_url}"
                        elif logo_url.startswith("/"):
                            logo_url = f"{base_url}{logo_url}"
                        elif not logo_url.startswith(("http://", "https://")):
                            path_base = "/".join(page.url.split("/")[:-1])
                            logo_url = f"{path_base}/{logo_url}"
                        
                        # Get format
                        format = logo_url.split(".")[-1].lower() if "." in logo_url else "unknown"
                        if format not in ["jpg", "jpeg", "png", "gif", "svg", "webp"]:
                            format = "unknown"
                        
                        # Create logo object
                        logo = Logo(
                            url=page.url,
                            src=logo_url,
                            alt="Schema.org Logo",
                            width=None,
                            height=None,
                            format=format,
                        )
                        logos.append(logo)
            except Exception as e:
                logger.warning(f"Error parsing schema.org data: {e}")
        
        return logos
    
    def _score_and_rank_logos(self, logos: List[Logo]) -> List[Logo]:
        """Score and rank logos based on various heuristics."""
        scored_logos = []
        
        for logo in logos:
            score = 0
            
            # Score based on filename
            if "logo" in logo.src.lower():
                score += 10
            if "brand" in logo.src.lower():
                score += 5
            if "header" in logo.src.lower():
                score += 3
            if "icon" in logo.src.lower():
                score += 2
            
            # Score based on alt text
            if logo.alt:
                if "logo" in logo.alt.lower():
                    score += 8
                if "brand" in logo.alt.lower():
                    score += 4
                if "company" in logo.alt.lower():
                    score += 3
                if "site" in logo.alt.lower() or "website" in logo.alt.lower():
                    score += 2
            
            # Score based on format
            if logo.format == "svg":
                score += 5  # SVG is often used for logos
            elif logo.format in ["png", "webp"]:
                score += 3  # PNG and WebP often support transparency
            
            # Score based on source
            if "schema.org" in logo.alt:
                score += 15  # Explicitly defined as logo in schema.org
            elif "favicon" in logo.alt:
                score += 1  # Favicon is a fallback
            elif "open graph" in logo.alt.lower():
                score += 2  # Open Graph image might be a logo
            
            # Add to scored logos
            scored_logos.append((logo, score))
        
        # Sort by score (descending)
        scored_logos.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicates while preserving order
        unique_logos = []
        seen_srcs = set()
        for logo, _ in scored_logos:
            if logo.src not in seen_srcs:
                seen_srcs.add(logo.src)
                unique_logos.append(logo)
        
        return unique_logos


class ColorExtractor:
    """Extracts colors from websites."""
    
    def __init__(self):
        """Initialize the color extractor."""
        self.image_processor = ImageProcessor()

    async def extract(
        self, page: Page, soup: BeautifulSoup, screenshot: bytes, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract colors from the page."""
        colors = []
        palette = {}
        options = options or {}

        try:
            logger.info("Extracting colors from website")
            
            # Extract colors from CSS
            logger.info("Extracting colors from CSS")
            css_colors = await self._extract_css_colors(page, soup, options.get("element_focus"))
            colors.extend(css_colors)
            
            # Extract colors from computed styles
            logger.info("Extracting colors from computed styles")
            computed_colors = await self._extract_computed_styles_colors(page, options.get("element_focus"))
            colors.extend(computed_colors)

            # Extract colors from screenshot
            logger.info("Extracting colors from screenshot")
            screenshot_colors = await self._extract_screenshot_colors(screenshot)
            colors.extend(screenshot_colors)
            
            # Extract colors from images
            if options.get("include_images", True):
                logger.info("Extracting colors from images")
                image_colors = await self._extract_image_colors(page, soup)
                colors.extend(image_colors)

            # Deduplicate and categorize colors
            logger.info("Deduplicating and categorizing colors")
            unique_colors = self._deduplicate_colors(colors)
            categorized = self._categorize_colors(unique_colors)
            
            # Create color relationships
            logger.info("Creating color relationships")
            relationships = self._create_color_relationships(unique_colors)
            
            # Build palette
            palette = {
                "primary": categorized.get("primary", []),
                "secondary": categorized.get("secondary", []),
                "accent": categorized.get("accent", []),
                "background": categorized.get("background", []),
                "text": categorized.get("text", []),
                "relationships": relationships,
            }
            
            logger.info(f"Found {len(unique_colors)} unique colors")
            return {"colors": unique_colors, "palette": palette}

        except Exception as e:
            logger.exception(f"Error extracting colors: {e}")
            return {"colors": [], "palette": {}}

    async def _extract_css_colors(
        self, page: Page, soup: BeautifulSoup, element_focus: Optional[str] = None
    ) -> List[Color]:
        """Extract colors from CSS stylesheets."""
        colors = []
        
        try:
            # Extract colors from stylesheets
            stylesheet_colors = await page.evaluate("""() => {
                const colors = [];
                const colorProps = [
                    'color', 'background-color', 'border-color', 'border-top-color',
                    'border-right-color', 'border-bottom-color', 'border-left-color',
                    'outline-color', 'text-decoration-color', 'fill', 'stroke'
                ];
                
                // Helper function to extract colors from CSS rules
                function extractColorsFromRules(rules) {
                    for (const rule of rules) {
                        // Handle media queries
                        if (rule.type === CSSRule.MEDIA_RULE) {
                            extractColorsFromRules(rule.cssRules);
                            continue;
                        }
                        
                        // Skip non-style rules
                        if (rule.type !== CSSRule.STYLE_RULE) continue;
                        
                        // Get selector and element type
                        const selector = rule.selectorText;
                        let elementType = 'unknown';
                        
                        // Try to determine element type from selector
                        if (/button|btn|\.button|\\[class\\*=button\\]/i.test(selector)) {
                            elementType = 'button';
                        } else if (/body|html|main|section|article|div|container/i.test(selector)) {
                            elementType = 'background';
                        } else if (/p|h[1-6]|span|a|text|font|link/i.test(selector)) {
                            elementType = 'text';
                        } else if (/header|nav|menu|navbar/i.test(selector)) {
                            elementType = 'header';
                        } else if (/footer/i.test(selector)) {
                            elementType = 'footer';
                        }
                        
                        // Extract colors from style properties
                        for (const prop of colorProps) {
                            const value = rule.style.getPropertyValue(prop);
                            if (value && value !== 'transparent' && value !== 'rgba(0, 0, 0, 0)') {
                                colors.push({
                                    value: value,
                                    property: prop,
                                    selector: selector,
                                    elementType: elementType
                                });
                            }
                        }
                    }
                }
                
                // Process all stylesheets
                try {
                    for (const sheet of document.styleSheets) {
                        try {
                            // Skip external stylesheets (CORS issues)
                            if (sheet.href && !sheet.href.startsWith(window.location.origin)) continue;
                            
                            // Extract colors from rules
                            extractColorsFromRules(sheet.cssRules || sheet.rules);
                        } catch (e) {
                            // CORS issues might prevent accessing some stylesheets
                            console.error("Error accessing stylesheet:", e);
                        }
                    }
                } catch (e) {
                    console.error("Error processing stylesheets:", e);
                }
                
                return colors;
            }""")
            
            # Process extracted colors
            for color_data in stylesheet_colors:
                color_obj = self._parse_color(color_data["value"])
                if color_obj:
                    color_obj.element_type = color_data["elementType"]
                    colors.append(color_obj)
            
            # Filter by element focus if specified
            if element_focus:
                colors = [c for c in colors if c.element_type == element_focus]
            
            return colors
            
        except Exception as e:
            logger.exception(f"Error extracting CSS colors: {e}")
            return []
            
    async def _extract_computed_styles_colors(
        self, page: Page, element_focus: Optional[str] = None
    ) -> List[Color]:
        """Extract colors from computed styles of DOM elements."""
        colors = []

        try:
            # Determine which elements to check based on focus
            elements_to_check = []
            
            if element_focus == "buttons":
                elements_to_check = await page.query_selector_all("button, .btn, [class*=button], input[type=button], input[type=submit]")
            elif element_focus == "backgrounds":
                elements_to_check = await page.query_selector_all("body, html, header, main, section, div[class*=container], .bg, [class*=background]")
            elif element_focus == "text":
                elements_to_check = await page.query_selector_all("p, h1, h2, h3, h4, h5, h6, span, a, label, li")
            else:
                # Check a representative sample of elements
                elements_to_check = await page.query_selector_all(`
                    body, html, header, footer, main, nav, section, article,
                    h1, h2, h3, p, a, button, .btn, input[type=button], input[type=submit],
                    .container, .bg, [class*=color], [class*=background], [class*=text],
                    .primary, .secondary, .accent, .highlight, .dark, .light
                `)

            # Process each element
            for element in elements_to_check:
                # Get computed styles with more color properties
                style = await page.evaluate("""(element) => {
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    const tagName = element.tagName.toLowerCase();
                    const classList = Array.from(element.classList).join(' ');
                    
                    // Determine element type
                    let elementType = 'unknown';
                    if (tagName === 'button' || classList.includes('btn') || classList.includes('button')) {
                        elementType = 'button';
                    } else if (tagName === 'body' || tagName === 'html' || tagName === 'main' || 
                               tagName === 'section' || tagName === 'div') {
                        elementType = 'background';
                    } else if (tagName === 'p' || tagName === 'span' || tagName === 'a' || 
                               tagName.startsWith('h') || tagName === 'label') {
                        elementType = 'text';
                    } else if (tagName === 'header' || tagName === 'nav') {
                        elementType = 'header';
                    } else if (tagName === 'footer') {
                        elementType = 'footer';
                    }
                    
                    // Get element size and visibility
                    const isVisible = style.display !== 'none' && 
                                     style.visibility !== 'hidden' && 
                                     rect.width > 0 && 
                                     rect.height > 0;
                    
                    // Get color properties
                    return {
                        color: style.color,
                        backgroundColor: style.backgroundColor,
                        borderColor: style.borderColor,
                        outlineColor: style.outlineColor,
                        textDecorationColor: style.textDecorationColor,
                        fill: style.fill,
                        stroke: style.stroke,
                        elementType: elementType,
                        isVisible: isVisible,
                        area: rect.width * rect.height,
                        inViewport: rect.top < window.innerHeight && rect.bottom > 0 &&
                                   rect.left < window.innerWidth && rect.right > 0
                    };
                }""", element)

                # Skip invisible elements
                if not style.get("isVisible", True):
                    continue
                
                # Process color properties
                for prop, value in style.items():
                    if prop in ["color", "backgroundColor", "borderColor", "outlineColor", 
                               "textDecorationColor", "fill", "stroke"]:
                        if value and value != "rgba(0, 0, 0, 0)" and value != "transparent":
                            color_obj = self._parse_color(value)
                            if color_obj:
                                # Set element type
                                if prop == "backgroundColor":
                                    color_obj.element_type = "background"
                                elif prop == "color":
                                    color_obj.element_type = "text"
                                elif prop in ["borderColor", "outlineColor"]:
                                    color_obj.element_type = "border"
                                else:
                                    color_obj.element_type = style.get("elementType", "unknown")
                                
                                # Adjust frequency based on element size and visibility
                                area_factor = min(1.0, style.get("area", 0) / 100000)  # Normalize area
                                viewport_bonus = 1.5 if style.get("inViewport", False) else 1.0
                                color_obj.frequency = color_obj.frequency * area_factor * viewport_bonus
                                
                                colors.append(color_obj)

            # Filter by element focus if specified
            if element_focus:
                colors = [c for c in colors if c.element_type == element_focus]
                
            return colors
            
        except Exception as e:
            logger.exception(f"Error extracting computed style colors: {e}")
            return []

    async def _extract_screenshot_colors(self, screenshot: bytes) -> List[Color]:
        """Extract dominant colors from screenshot."""
        colors = []

        try:
            # Extract dominant colors using image processor
            hex_colors = await self.image_processor.extract_dominant_colors(screenshot, num_colors=15)
            
            # Convert to Color objects
            for i, hex_color in enumerate(hex_colors):
                # Convert hex to RGB
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                rgb = (r, g, b)
                
                # Convert RGB to HSL
                hsl = self._rgb_to_hsl(rgb)
                
                # Create color object
                color = Color(
                    hex=hex_color,
                    rgb=rgb,
                    hsl=hsl,
                    frequency=1.0 - (i * 0.05),  # Approximate frequency based on palette order
                    element_type="screenshot",
                )
                colors.append(color)
                
            return colors
        except Exception as e:
            logger.exception(f"Error extracting colors from screenshot: {e}")
            return []
            
    async def _extract_image_colors(self, page: Page, soup: BeautifulSoup) -> List[Color]:
        """Extract colors from images on the page."""
        colors = []
        
        try:
            # Find significant images (logos, hero images, etc.)
            significant_images = await page.evaluate("""() => {
                const images = [];
                const allImages = document.querySelectorAll('img');
                
                for (const img of allImages) {
                    const rect = img.getBoundingClientRect();
                    
                    // Skip tiny or invisible images
                    if (rect.width < 50 || rect.height < 50 || 
                        img.style.display === 'none' || 
                        img.style.visibility === 'hidden') {
                        continue;
                    }
                    
                    // Calculate image area and position
                    const area = rect.width * rect.height;
                    const inViewport = rect.top < window.innerHeight && rect.bottom > 0 &&
                                      rect.left < window.innerWidth && rect.right > 0;
                    
                    // Check if image is significant
                    const isHero = rect.width > window.innerWidth * 0.5 && 
                                  rect.top < window.innerHeight * 0.5;
                    const isLogo = img.alt && img.alt.toLowerCase().includes('logo');
                    const isBanner = rect.width > window.innerWidth * 0.7 && 
                                    rect.height < window.innerHeight * 0.3;
                    
                    // Add significant images
                    if (isHero || isLogo || isBanner || area > 40000) {
                        images.push({
                            src: img.src,
                            area: area,
                            inViewport: inViewport,
                            isHero: isHero,
                            isLogo: isLogo,
                            isBanner: isBanner
                        });
                    }
                }
                
                // Sort by area (largest first) and limit to top 5
                return images.sort((a, b) => b.area - a.area).slice(0, 5);
            }""")
            
            # Process each significant image
            for img_data in significant_images:
                try:
                    # Skip data URLs (already processed)
                    if img_data["src"].startswith("data:"):
                        continue
                    
                    # Fetch and process image
                    image_info = await self.image_processor.fetch_and_process_image(img_data["src"])
                    
                    # Skip failed images
                    if image_info["error"] or not image_info["data"]:
                        continue
                    
                    # Extract colors from image
                    if image_info["data"].startswith("data:image/"):
                        # Get binary data from data URL
                        data_url_parts = image_info["data"].split(",")
                        if len(data_url_parts) > 1:
                            binary_data = base64.b64decode(data_url_parts[1])
                            
                            # Extract colors
                            hex_colors = await self.image_processor.extract_dominant_colors(binary_data, num_colors=5)
                            
                            # Convert to Color objects
                            for i, hex_color in enumerate(hex_colors):
                                # Convert hex to RGB
                                r = int(hex_color[1:3], 16)
                                g = int(hex_color[3:5], 16)
                                b = int(hex_color[5:7], 16)
                                rgb = (r, g, b)
                                
                                # Convert RGB to HSL
                                hsl = self._rgb_to_hsl(rgb)
                                
                                # Determine element type
                                element_type = "image"
                                if img_data.get("isLogo"):
                                    element_type = "logo"
                                elif img_data.get("isHero"):
                                    element_type = "hero"
                                elif img_data.get("isBanner"):
                                    element_type = "banner"
                                
                                # Create color object
                                color = Color(
                                    hex=hex_color,
                                    rgb=rgb,
                                    hsl=hsl,
                                    frequency=0.8 - (i * 0.1),  # Slightly lower than screenshot colors
                                    element_type=element_type,
                                )
                                colors.append(color)
                
                except Exception as e:
                    logger.warning(f"Error processing image {img_data['src']}: {e}")
            
            return colors
            
        except Exception as e:
            logger.exception(f"Error extracting colors from images: {e}")
            return []

    def _parse_color(self, color_str: str) -> Optional[Color]:
        """Parse color string into Color object."""
        # RGB/RGBA format
        rgb_match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)", color_str)
        if rgb_match:
            r = int(rgb_match.group(1))
            g = int(rgb_match.group(2))
            b = int(rgb_match.group(3))
            rgb = (r, g, b)
            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            hsl = self._rgb_to_hsl(rgb)
            return Color(hex=hex_color, rgb=rgb, hsl=hsl, frequency=1.0)

        # HEX format
        hex_match = re.match(r"#([0-9a-fA-F]{3,6})", color_str)
        if hex_match:
            hex_color = color_str.lower()
            if len(hex_color) == 4:  # #RGB format
                r = int(hex_color[1] + hex_color[1], 16)
                g = int(hex_color[2] + hex_color[2], 16)
                b = int(hex_color[3] + hex_color[3], 16)
            else:  # #RRGGBB format
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
            rgb = (r, g, b)
            hsl = self._rgb_to_hsl(rgb)
            return Color(hex=hex_color, rgb=rgb, hsl=hsl, frequency=1.0)

        return None

    def _rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Convert RGB to HSL color space."""
        r, g, b = rgb
        r /= 255
        g /= 255
        b /= 255
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        l = (max_val + min_val) / 2
        
        if max_val == min_val:
            h = s = 0  # achromatic
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        
        return (int(h * 360), int(s * 100), int(l * 100))

    def _deduplicate_colors(self, colors: List[Color]) -> List[Color]:
        """Remove duplicate colors and calculate frequency."""
        color_map = {}
        total = len(colors)
        
        for color in colors:
            if color.hex in color_map:
                color_map[color.hex]["count"] += 1
                if color.element_type and color.element_type not in color_map[color.hex]["element_types"]:
                    color_map[color.hex]["element_types"].append(color.element_type)
            else:
                color_map[color.hex] = {
                    "color": color,
                    "count": 1,
                    "element_types": [color.element_type] if color.element_type else []
                }
        
        result = []
        for hex_color, data in color_map.items():
            color = data["color"]
            color.frequency = data["count"] / total
            if data["element_types"]:
                color.element_type = data["element_types"][0]  # Use the first element type
            result.append(color)
        
        # Sort by frequency
        result.sort(key=lambda x: x.frequency, reverse=True)
        return result

    def _categorize_colors(self, colors: List[Color]) -> Dict[str, List[Color]]:
        """Categorize colors by their likely usage."""
        categories = {
            "primary": [],
            "secondary": [],
            "accent": [],
            "background": [],
            "text": [],
        }
        
        for color in colors:
            h, s, l = color.hsl
            
            # Categorize by element type if available
            if color.element_type:
                if color.element_type in ["background", "bg"]:
                    categories["background"].append(color)
                elif color.element_type in ["text", "color"]:
                    categories["text"].append(color)
                elif color.element_type in ["border"]:
                    categories["accent"].append(color)
                else:
                    # Default categorization by HSL values
                    self._categorize_by_hsl(color, categories)
            else:
                # Categorize by HSL values
                self._categorize_by_hsl(color, categories)
        
        return categories

    def _categorize_by_hsl(self, color: Color, categories: Dict[str, List[Color]]) -> None:
        """Categorize a color by its HSL values."""
        h, s, l = color.hsl
        
        # Very dark colors are likely text
        if l < 20:
            categories["text"].append(color)
        # Very light colors are likely backgrounds
        elif l > 90:
            categories["background"].append(color)
        # Highly saturated colors are likely accents or primary
        elif s > 70:
            if color.frequency > 0.1:
                categories["primary"].append(color)
            else:
                categories["accent"].append(color)
        # Medium saturation colors could be primary or secondary
        elif s > 30:
            if color.frequency > 0.1:
                categories["primary"].append(color)
            else:
                categories["secondary"].append(color)
        # Low saturation colors are likely backgrounds or text
        else:
            if l > 50:
                categories["background"].append(color)
            else:
                categories["text"].append(color)


class UIStyleExtractor:
    """Extracts UI styling information from websites."""

    async def extract(
        self, page: Page, soup: BeautifulSoup, options: Optional[Dict[str, Any]] = None
    ) -> UIStyle:
        """Extract UI styling information from the page."""
        options = options or {}
        component_types = options.get("component_types", [])
        
        try:
            # Extract typography
            typography = await self._extract_typography(page, soup)
            
            # Extract spacing
            spacing = await self._extract_spacing(page)
            
            # Extract component styles
            components = await self._extract_components(page, component_types)
            
            # Detect frameworks
            frameworks = await self._detect_frameworks(page)
            
            # Extract breakpoints
            breakpoints = await self._extract_breakpoints(page)
            
            return UIStyle(
                typography=typography,
                spacing=spacing,
                components=components,
                frameworks=frameworks,
                breakpoints=breakpoints,
            )
        
        except Exception as e:
            logger.exception(f"Error extracting UI styles: {e}")
            return UIStyle(
                typography=[],
                spacing={},
                components=[],
                frameworks=[],
                breakpoints={},
            )

    async def _extract_typography(self, page: Page, soup: BeautifulSoup) -> List[Typography]:
        """Extract typography information."""
        typography = []
        
        # Get all text elements
        text_elements = {
            "heading": ["h1", "h2", "h3", "h4", "h5", "h6"],
            "paragraph": ["p"],
            "button": ["button"],
            "link": ["a"],
            "label": ["label"],
        }
        
        for element_type, selectors in text_elements.items():
            selector = ", ".join(selectors)
            elements = await page.query_selector_all(selector)
            
            font_families = {}
            sizes = []
            weights = []
            line_heights = []
            
            for element in elements:
                # Get computed styles
                style = await page.evaluate("""(element) => {
                    const style = window.getComputedStyle(element);
                    return {
                        fontFamily: style.fontFamily,
                        fontSize: parseInt(style.fontSize),
                        fontWeight: parseInt(style.fontWeight),
                        lineHeight: parseFloat(style.lineHeight) / parseFloat(style.fontSize)
                    };
                }""", element)
                
                # Process font family
                font_family = style["fontFamily"].split(",")[0].strip().strip('"\'')
                if font_family:
                    if font_family in font_families:
                        font_families[font_family] += 1
                    else:
                        font_families[font_family] = 1
                
                # Process other properties
                if style["fontSize"]:
                    sizes.append(style["fontSize"])
                if style["fontWeight"]:
                    weights.append(style["fontWeight"])
                if style["lineHeight"]:
                    line_heights.append(style["lineHeight"])
            
            # Create typography object if we have data
            if font_families:
                # Get most common font family
                font_family = max(font_families.items(), key=lambda x: x[1])[0]
                
                # Remove duplicates and sort
                sizes = sorted(list(set(sizes)))
                weights = sorted(list(set(weights)))
                line_heights = sorted(list(set(line_heights)))
                
                typography.append(Typography(
                    font_family=font_family,
                    sizes=sizes,
                    weights=weights,
                    line_heights=line_heights,
                    element_types=[element_type],
                ))
        
        return typography

    async def _extract_spacing(self, page: Page) -> Dict[str, List[int]]:
        """Extract spacing patterns."""
        spacing = {
            "margin": [],
            "padding": [],
            "gap": [],
        }
        
        # Get common container elements
        elements = await page.query_selector_all("body, main, section, div[class*=container], header, footer")
        
        for element in elements:
            # Get computed styles
            style = await page.evaluate("""(element) => {
                const style = window.getComputedStyle(element);
                return {
                    marginTop: parseInt(style.marginTop),
                    marginBottom: parseInt(style.marginBottom),
                    marginLeft: parseInt(style.marginLeft),
                    marginRight: parseInt(style.marginRight),
                    paddingTop: parseInt(style.paddingTop),
                    paddingBottom: parseInt(style.paddingBottom),
                    paddingLeft: parseInt(style.paddingLeft),
                    paddingRight: parseInt(style.paddingRight),
                    gap: parseInt(style.gap) || 0
                };
            }""", element)
            
            # Process margins
            for prop in ["marginTop", "marginBottom", "marginLeft", "marginRight"]:
                if style[prop] and style[prop] > 0:
                    spacing["margin"].append(style[prop])
            
            # Process paddings
            for prop in ["paddingTop", "paddingBottom", "paddingLeft", "paddingRight"]:
                if style[prop] and style[prop] > 0:
                    spacing["padding"].append(style[prop])
            
            # Process gap
            if style["gap"] and style["gap"] > 0:
                spacing["gap"].append(style["gap"])
        
        # Remove duplicates and sort
        for key in spacing:
            spacing[key] = sorted(list(set(spacing[key])))
        
        return spacing

    async def _extract_components(self, page: Page, component_types: List[str]) -> List[ComponentStyle]:
        """Extract component styles."""
        components = []
        
        # Define component selectors
        component_selectors = {
            "button": "button, .btn, [class*=button]",
            "form": "form, input, select, textarea",
            "card": ".card, [class*=card], .box, [class*=box]",
            "nav": "nav, .nav, [class*=nav], .menu, [class*=menu]",
            "table": "table, .table, [class*=table]",
            "modal": ".modal, [class*=modal], .dialog, [class*=dialog]",
        }
        
        # Filter by requested component types if specified
        if component_types:
            component_selectors = {k: v for k, v in component_selectors.items() if k in component_types}
        
        for component_type, selector in component_selectors.items():
            elements = await page.query_selector_all(selector)
            
            if not elements:
                continue
            
            # Get first element for analysis
            element = elements[0]
            
            # Get computed styles
            css_properties = await page.evaluate("""(element) => {
                const style = window.getComputedStyle(element);
                const properties = {};
                
                // Extract relevant CSS properties
                const relevantProps = [
                    'backgroundColor', 'color', 'borderRadius', 'border',
                    'padding', 'margin', 'boxShadow', 'fontFamily',
                    'fontSize', 'fontWeight', 'textAlign', 'display',
                    'flexDirection', 'alignItems', 'justifyContent'
                ];
                
                for (const prop of relevantProps) {
                    properties[prop] = style[prop];
                }
                
                return properties;
            }""", element)
            
            # Create component style object
            components.append(ComponentStyle(
                type=component_type,
                css_properties=css_properties,
            ))
        
        return components

    async def _detect_frameworks(self, page: Page) -> List[str]:
        """Detect CSS frameworks used on the page."""
        frameworks = []
        
        # Check for common frameworks
        framework_signatures = {
            "Bootstrap": [".navbar-nav", ".container-fluid", ".row", ".col-", "bootstrap"],
            "Tailwind CSS": ["[class*='text-']", "[class*='bg-']", "[class*='p-']", "[class*='m-']", "tailwind"],
            "Material UI": [".MuiButton", ".MuiPaper", ".MuiTypography", "material-ui"],
            "Bulma": [".is-primary", ".is-info", ".columns", ".column", "bulma"],
            "Foundation": [".button", ".callout", ".grid-x", ".cell", "foundation"],
            "Semantic UI": [".ui.button", ".ui.menu", ".ui.grid", ".ui.segment", "semantic"],
        }
        
        for framework, signatures in framework_signatures.items():
            for signature in signatures:
                elements = await page.query_selector_all(signature)
                if elements:
                    frameworks.append(framework)
                    break
        
        # Check for framework in meta tags or script tags
        framework_keywords = ["bootstrap", "tailwind", "material", "bulma", "foundation", "semantic"]
        
        meta_content = await page.evaluate("""() => {
            const metas = document.querySelectorAll('meta[name="generator"], meta[content*="framework"]');
            const scripts = document.querySelectorAll('script[src]');
            const links = document.querySelectorAll('link[href][rel="stylesheet"]');
            
            let content = '';
            
            metas.forEach(meta => content += meta.getAttribute('content') + ' ');
            scripts.forEach(script => content += script.getAttribute('src') + ' ');
            links.forEach(link => content += link.getAttribute('href') + ' ');
            
            return content.toLowerCase();
        }""")
        
        for keyword in framework_keywords:
            if keyword in meta_content and not any(framework.lower() in keyword for framework in frameworks):
                if keyword == "bootstrap":
                    frameworks.append("Bootstrap")
                elif keyword == "tailwind":
                    frameworks.append("Tailwind CSS")
                elif keyword == "material":
                    frameworks.append("Material UI")
                elif keyword == "bulma":
                    frameworks.append("Bulma")
                elif keyword == "foundation":
                    frameworks.append("Foundation")
                elif keyword == "semantic":
                    frameworks.append("Semantic UI")
        
        return list(set(frameworks))

    async def _extract_breakpoints(self, page: Page) -> Dict[str, int]:
        """Extract responsive breakpoints."""
        breakpoints = {}
        
        # Get media queries from stylesheets
        media_queries = await page.evaluate("""() => {
            const breakpoints = {};
            const sheets = document.styleSheets;
            
            try {
                for (let i = 0; i < sheets.length; i++) {
                    const rules = sheets[i].cssRules || sheets[i].rules;
                    if (!rules) continue;
                    
                    for (let j = 0; j < rules.length; j++) {
                        const rule = rules[j];
                        if (rule.type === CSSRule.MEDIA_RULE) {
                            const mediaText = rule.conditionText || rule.media.mediaText;
                            
                            // Extract min-width and max-width values
                            const minWidthMatch = mediaText.match(/min-width:\s*(\d+)px/);
                            const maxWidthMatch = mediaText.match(/max-width:\s*(\d+)px/);
                            
                            if (minWidthMatch) {
                                const width = parseInt(minWidthMatch[1]);
                                breakpoints['min-' + width] = width;
                            }
                            
                            if (maxWidthMatch) {
                                const width = parseInt(maxWidthMatch[1]);
                                breakpoints['max-' + width] = width;
                            }
                        }
                    }
                }
            } catch (e) {
                // CORS issues might prevent accessing some stylesheets
                console.error("Error accessing stylesheets:", e);
            }
            
            return breakpoints;
        }""")
        
        # Identify common breakpoint patterns
        common_breakpoints = {
            "xs": 0,
            "sm": 576,
            "md": 768,
            "lg": 992,
            "xl": 1200,
            "xxl": 1400,
        }
        
        # Merge extracted breakpoints with common patterns
        for name, width in common_breakpoints.items():
            if f"min-{width}" in media_queries or f"max-{width}" in media_queries:
                breakpoints[name] = width
        
        # Add any other breakpoints found
        for key, value in media_queries.items():
            if key.startswith("min-") or key.startswith("max-"):
                size_name = key
                if key not in breakpoints:
                    breakpoints[size_name] = value
        
        return breakpoints