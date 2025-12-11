"""Tests for the extractors module."""

import asyncio
import base64
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.extractors import (
    ColorExtractor,
    LogoExtractor,
    UIStyleExtractor,
)
from website_scraper_mcp.models import Color, Logo, Typography, UIStyle


class TestLogoExtractor(unittest.TestCase):
    """Test the LogoExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = LogoExtractor()
        self.extractor.image_processor = MagicMock()
        self.extractor.image_processor.fetch_and_process_image = AsyncMock()

    async def test_extract_with_selector(self):
        """Test extracting logos with a selector."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_soup = MagicMock()
        
        # Mock soup.select to return a logo element
        mock_img = MagicMock()
        mock_img.name = "img"
        mock_img.get.side_effect = lambda attr, default="": {
            "src": "https://example.com/logo.png",
            "alt": "Example Logo",
            "width": "100",
            "height": "50",
        }.get(attr, default)
        mock_soup.select.return_value = [mock_img]
        
        # Mock page.url
        mock_page.url = "https://example.com"
        
        # Mock image processor
        self.extractor.image_processor.fetch_and_process_image.return_value = {
            "data": "data:image/png;base64,abc123",
            "width": 100,
            "height": 50,
            "format": "png",
            "error": None,
        }
        
        # Call extract with selector
        logos = await self.extractor.extract(mock_page, mock_soup, selector=".logo")
        
        # Verify soup.select was called with the selector
        mock_soup.select.assert_called_once_with(".logo")
        
        # Verify image processor was called
        self.extractor.image_processor.fetch_and_process_image.assert_called_once_with("https://example.com/logo.png")
        
        # Verify result
        self.assertEqual(len(logos), 1)
        self.assertEqual(logos[0].url, "https://example.com")
        self.assertEqual(logos[0].src, "https://example.com/logo.png")
        self.assertEqual(logos[0].alt, "Example Logo")
        self.assertEqual(logos[0].width, 100)
        self.assertEqual(logos[0].height, 50)
        self.assertEqual(logos[0].format, "png")
        self.assertEqual(logos[0].data, "data:image/png;base64,abc123")

    @patch.object(LogoExtractor, "_find_logo_elements")
    @patch.object(LogoExtractor, "_process_logo_elements")
    @patch.object(LogoExtractor, "_try_additional_logo_strategies")
    @patch.object(LogoExtractor, "_score_and_rank_logos")
    async def test_extract_without_selector(
        self, mock_score, mock_try_additional, mock_process, mock_find
    ):
        """Test extracting logos without a selector."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_soup = MagicMock()
        
        # Mock _find_logo_elements to return elements
        mock_elements = [MagicMock(), MagicMock()]
        mock_find.return_value = mock_elements
        
        # Mock _process_logo_elements to return logos
        mock_logos = [
            Logo(url="https://example.com", src="https://example.com/logo1.png", format="png"),
            Logo(url="https://example.com", src="https://example.com/logo2.png", format="png"),
        ]
        mock_process.return_value = mock_logos
        
        # Mock _score_and_rank_logos to return scored logos
        mock_score.return_value = mock_logos
        
        # Call extract without selector
        logos = await self.extractor.extract(mock_page, mock_soup)
        
        # Verify _find_logo_elements was called
        mock_find.assert_called_once_with(mock_page, mock_soup)
        
        # Verify _process_logo_elements was called with the elements
        mock_process.assert_called_once_with(mock_page, mock_elements)
        
        # Verify _score_and_rank_logos was called with the logos
        mock_score.assert_called_once_with(mock_logos)
        
        # Verify _try_additional_logo_strategies was not called
        mock_try_additional.assert_not_called()
        
        # Verify result
        self.assertEqual(logos, mock_logos)

    @patch.object(LogoExtractor, "_find_logo_elements")
    @patch.object(LogoExtractor, "_process_logo_elements")
    @patch.object(LogoExtractor, "_try_additional_logo_strategies")
    @patch.object(LogoExtractor, "_score_and_rank_logos")
    async def test_extract_no_logos_found(
        self, mock_score, mock_try_additional, mock_process, mock_find
    ):
        """Test extracting logos when none are found."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_soup = MagicMock()
        
        # Mock _find_logo_elements to return elements
        mock_elements = [MagicMock(), MagicMock()]
        mock_find.return_value = mock_elements
        
        # Mock _process_logo_elements to return no logos
        mock_process.return_value = []
        
        # Mock _try_additional_logo_strategies to return logos
        mock_additional_logos = [
            Logo(url="https://example.com", src="https://example.com/favicon.ico", format="ico"),
        ]
        mock_try_additional.return_value = mock_additional_logos
        
        # Mock _score_and_rank_logos to return scored logos
        mock_score.return_value = mock_additional_logos
        
        # Call extract without selector
        logos = await self.extractor.extract(mock_page, mock_soup)
        
        # Verify _find_logo_elements was called
        mock_find.assert_called_once_with(mock_page, mock_soup)
        
        # Verify _process_logo_elements was called with the elements
        mock_process.assert_called_once_with(mock_page, mock_elements)
        
        # Verify _try_additional_logo_strategies was called
        mock_try_additional.assert_called_once_with(mock_page, mock_soup)
        
        # Verify _score_and_rank_logos was called with the additional logos
        mock_score.assert_called_once_with(mock_additional_logos)
        
        # Verify result
        self.assertEqual(logos, mock_additional_logos)


class TestColorExtractor(unittest.TestCase):
    """Test the ColorExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = ColorExtractor()
        self.extractor.image_processor = MagicMock()
        self.extractor.image_processor.extract_dominant_colors = AsyncMock()

    @patch.object(ColorExtractor, "_extract_css_colors")
    @patch.object(ColorExtractor, "_extract_computed_styles_colors")
    @patch.object(ColorExtractor, "_extract_screenshot_colors")
    @patch.object(ColorExtractor, "_extract_image_colors")
    @patch.object(ColorExtractor, "_deduplicate_colors")
    @patch.object(ColorExtractor, "_categorize_colors")
    @patch.object(ColorExtractor, "_create_color_relationships")
    async def test_extract(
        self, mock_relationships, mock_categorize, mock_deduplicate,
        mock_image_colors, mock_screenshot_colors, mock_computed_colors, mock_css_colors
    ):
        """Test extracting colors."""
        # Mock page, soup, and screenshot
        mock_page = AsyncMock()
        mock_soup = MagicMock()
        mock_screenshot = b"screenshot_data"
        
        # Mock options
        mock_options = {"element_focus": "buttons", "include_images": True}
        
        # Mock color extraction methods
        css_colors = [
            Color(hex="#ff0000", rgb=(255, 0, 0), hsl=(0, 100, 50), frequency=0.5),
            Color(hex="#00ff00", rgb=(0, 255, 0), hsl=(120, 100, 50), frequency=0.3),
        ]
        computed_colors = [
            Color(hex="#0000ff", rgb=(0, 0, 255), hsl=(240, 100, 50), frequency=0.2),
        ]
        screenshot_colors = [
            Color(hex="#ffff00", rgb=(255, 255, 0), hsl=(60, 100, 50), frequency=0.4),
        ]
        image_colors = [
            Color(hex="#ff00ff", rgb=(255, 0, 255), hsl=(300, 100, 50), frequency=0.1),
        ]
        
        mock_css_colors.return_value = css_colors
        mock_computed_colors.return_value = computed_colors
        mock_screenshot_colors.return_value = screenshot_colors
        mock_image_colors.return_value = image_colors
        
        # Mock deduplicate and categorize
        unique_colors = css_colors + computed_colors + screenshot_colors + image_colors
        mock_deduplicate.return_value = unique_colors
        
        categorized_colors = {
            "primary": [css_colors[0]],
            "secondary": [css_colors[1]],
            "accent": [computed_colors[0]],
            "background": [screenshot_colors[0]],
            "text": [image_colors[0]],
        }
        mock_categorize.return_value = categorized_colors
        
        # Mock relationships
        relationships = {"complementary": [css_colors[0], css_colors[1]]}
        mock_relationships.return_value = relationships
        
        # Call extract
        result = await self.extractor.extract(mock_page, mock_soup, mock_screenshot, mock_options)
        
        # Verify extraction methods were called
        mock_css_colors.assert_called_once_with(mock_page, mock_soup, "buttons")
        mock_computed_colors.assert_called_once_with(mock_page, "buttons")
        mock_screenshot_colors.assert_called_once_with(mock_screenshot)
        mock_image_colors.assert_called_once_with(mock_page, mock_soup)
        
        # Verify deduplicate and categorize were called
        all_colors = css_colors + computed_colors + screenshot_colors + image_colors
        mock_deduplicate.assert_called_once()
        mock_categorize.assert_called_once_with(unique_colors)
        mock_relationships.assert_called_once_with(unique_colors)
        
        # Verify result
        self.assertEqual(result["colors"], unique_colors)
        self.assertEqual(result["palette"]["primary"], categorized_colors["primary"])
        self.assertEqual(result["palette"]["secondary"], categorized_colors["secondary"])
        self.assertEqual(result["palette"]["accent"], categorized_colors["accent"])
        self.assertEqual(result["palette"]["background"], categorized_colors["background"])
        self.assertEqual(result["palette"]["text"], categorized_colors["text"])
        self.assertEqual(result["palette"]["relationships"], relationships)

    def test_parse_color_rgb(self):
        """Test parsing RGB color strings."""
        # Test RGB format
        color = self.extractor._parse_color("rgb(255, 0, 0)")
        self.assertIsNotNone(color)
        self.assertEqual(color.hex, "#ff0000")
        self.assertEqual(color.rgb, (255, 0, 0))
        self.assertEqual(color.hsl[0], 0)  # Hue
        
        # Test RGBA format
        color = self.extractor._parse_color("rgba(0, 255, 0, 0.5)")
        self.assertIsNotNone(color)
        self.assertEqual(color.hex, "#00ff00")
        self.assertEqual(color.rgb, (0, 255, 0))
        self.assertEqual(color.hsl[0], 120)  # Hue

    def test_parse_color_hex(self):
        """Test parsing HEX color strings."""
        # Test 6-digit HEX format
        color = self.extractor._parse_color("#0000ff")
        self.assertIsNotNone(color)
        self.assertEqual(color.hex, "#0000ff")
        self.assertEqual(color.rgb, (0, 0, 255))
        self.assertEqual(color.hsl[0], 240)  # Hue
        
        # Test 3-digit HEX format
        color = self.extractor._parse_color("#f00")
        self.assertIsNotNone(color)
        self.assertEqual(color.hex, "#ff0000")
        self.assertEqual(color.rgb, (255, 0, 0))
        self.assertEqual(color.hsl[0], 0)  # Hue

    def test_rgb_to_hsl(self):
        """Test converting RGB to HSL."""
        # Test red
        hsl = self.extractor._rgb_to_hsl((255, 0, 0))
        self.assertEqual(hsl[0], 0)  # Hue
        self.assertEqual(hsl[1], 100)  # Saturation
        self.assertEqual(hsl[2], 50)  # Lightness
        
        # Test green
        hsl = self.extractor._rgb_to_hsl((0, 255, 0))
        self.assertEqual(hsl[0], 120)  # Hue
        self.assertEqual(hsl[1], 100)  # Saturation
        self.assertEqual(hsl[2], 50)  # Lightness
        
        # Test blue
        hsl = self.extractor._rgb_to_hsl((0, 0, 255))
        self.assertEqual(hsl[0], 240)  # Hue
        self.assertEqual(hsl[1], 100)  # Saturation
        self.assertEqual(hsl[2], 50)  # Lightness
        
        # Test white
        hsl = self.extractor._rgb_to_hsl((255, 255, 255))
        self.assertEqual(hsl[2], 100)  # Lightness
        
        # Test black
        hsl = self.extractor._rgb_to_hsl((0, 0, 0))
        self.assertEqual(hsl[2], 0)  # Lightness


class TestUIStyleExtractor(unittest.TestCase):
    """Test the UIStyleExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = UIStyleExtractor()

    @patch.object(UIStyleExtractor, "_extract_typography")
    @patch.object(UIStyleExtractor, "_extract_spacing")
    @patch.object(UIStyleExtractor, "_extract_components")
    @patch.object(UIStyleExtractor, "_detect_frameworks")
    @patch.object(UIStyleExtractor, "_extract_breakpoints")
    async def test_extract(
        self, mock_breakpoints, mock_frameworks, mock_components, mock_spacing, mock_typography
    ):
        """Test extracting UI styles."""
        # Mock page and soup
        mock_page = AsyncMock()
        mock_soup = MagicMock()
        
        # Mock options
        mock_options = {"component_types": ["button", "form"]}
        
        # Mock extraction methods
        typography = [
            Typography(
                font_family="Arial",
                sizes=[16, 24],
                weights=[400, 700],
                line_heights=[1.5, 2.0],
                element_types=["heading"],
            ),
            Typography(
                font_family="Helvetica",
                sizes=[14, 16],
                weights=[400],
                line_heights=[1.5],
                element_types=["paragraph"],
            ),
        ]
        spacing = {
            "margin": [8, 16, 24],
            "padding": [8, 16],
            "gap": [8],
        }
        components = [
            MagicMock(type="button"),
            MagicMock(type="form"),
        ]
        frameworks = ["Bootstrap", "jQuery"]
        breakpoints = {
            "sm": 576,
            "md": 768,
            "lg": 992,
            "xl": 1200,
        }
        
        mock_typography.return_value = typography
        mock_spacing.return_value = spacing
        mock_components.return_value = components
        mock_frameworks.return_value = frameworks
        mock_breakpoints.return_value = breakpoints
        
        # Call extract
        result = await self.extractor.extract(mock_page, mock_soup, mock_options)
        
        # Verify extraction methods were called
        mock_typography.assert_called_once_with(mock_page, mock_soup)
        mock_spacing.assert_called_once_with(mock_page)
        mock_components.assert_called_once_with(mock_page, ["button", "form"])
        mock_frameworks.assert_called_once_with(mock_page)
        mock_breakpoints.assert_called_once_with(mock_page)
        
        # Verify result
        self.assertEqual(result.typography, typography)
        self.assertEqual(result.spacing, spacing)
        self.assertEqual(result.components, components)
        self.assertEqual(result.frameworks, frameworks)
        self.assertEqual(result.breakpoints, breakpoints)


if __name__ == "__main__":
    # Run tests
    unittest.main()