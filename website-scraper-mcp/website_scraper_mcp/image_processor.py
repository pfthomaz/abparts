"""Image processing module for the Website Scraper MCP Server."""

import asyncio
import base64
import io
import logging
import re
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import colorthief
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes images for extraction of visual elements."""

    def __init__(self) -> None:
        """Initialize the image processor."""
        self.session = None
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 "
            "Website-Scraper-MCP/0.1.0"
        )
        self._image_cache = {}  # Cache for fetched images

    async def fetch_and_process_image(self, url: str) -> Dict[str, Any]:
        """Fetch and process an image from a URL."""
        # Check cache first
        if url in self._image_cache:
            return self._image_cache[url]

        # Initialize result
        result = {
            "data": None,
            "width": None,
            "height": None,
            "format": None,
            "error": None,
        }

        try:
            # Handle data URLs
            if url.startswith("data:image/"):
                return await self._process_data_url(url)

            # Create session if needed
            if self.session is None:
                self.session = aiohttp.ClientSession(
                    headers={"User-Agent": self.user_agent}
                )

            # Fetch image
            async with self.session.get(url, timeout=10) as response:
                if response.status != 200:
                    result["error"] = f"Failed to fetch image: HTTP {response.status}"
                    return result

                # Get content type
                content_type = response.headers.get("Content-Type", "")
                if not content_type.startswith("image/"):
                    result["error"] = f"Not an image: {content_type}"
                    return result

                # Read image data
                image_data = await response.read()

                # Process image
                return await self._process_image_data(image_data, content_type)

        except aiohttp.ClientError as e:
            result["error"] = f"Network error: {str(e)}"
            return result
        except asyncio.TimeoutError:
            result["error"] = "Timeout fetching image"
            return result
        except Exception as e:
            result["error"] = f"Error processing image: {str(e)}"
            return result

    async def _process_data_url(self, data_url: str) -> Dict[str, Any]:
        """Process an image from a data URL."""
        result = {
            "data": data_url,
            "width": None,
            "height": None,
            "format": None,
            "error": None,
        }

        try:
            # Parse data URL
            match = re.match(r"data:image/([a-zA-Z0-9]+);base64,(.+)", data_url)
            if not match:
                result["error"] = "Invalid data URL format"
                return result

            # Extract format and data
            result["format"] = match.group(1)
            base64_data = match.group(2)

            # Decode base64 data
            image_data = base64.b64decode(base64_data)

            # Get image dimensions
            with Image.open(io.BytesIO(image_data)) as img:
                result["width"] = img.width
                result["height"] = img.height

            return result

        except Exception as e:
            result["error"] = f"Error processing data URL: {str(e)}"
            return result

    async def _process_image_data(
        self, image_data: bytes, content_type: str
    ) -> Dict[str, Any]:
        """Process image data."""
        result = {
            "data": None,
            "width": None,
            "height": None,
            "format": None,
            "error": None,
        }

        try:
            # Get format from content type
            format_match = re.match(r"image/([a-zA-Z0-9]+)", content_type)
            if format_match:
                result["format"] = format_match.group(1)
            else:
                result["format"] = "unknown"

            # Get image dimensions
            with Image.open(io.BytesIO(image_data)) as img:
                result["width"] = img.width
                result["height"] = img.height

                # Convert to data URL
                img_byte_arr = io.BytesIO()
                
                # Preserve SVG format
                if result["format"].lower() == "svg+xml":
                    result["data"] = f"data:{content_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
                else:
                    # For other formats, use PIL to save as PNG
                    if img.mode == "RGBA":
                        img.save(img_byte_arr, format="PNG")
                        result["format"] = "png"
                    else:
                        img.save(img_byte_arr, format="JPEG", quality=85)
                        result["format"] = "jpeg"
                    
                    img_byte_arr = img_byte_arr.getvalue()
                    result["data"] = f"data:image/{result['format']};base64,{base64.b64encode(img_byte_arr).decode('utf-8')}"

            # Cache result
            self._image_cache[f"data:image/{result['format']};base64,..."] = result

            return result

        except Exception as e:
            result["error"] = f"Error processing image data: {str(e)}"
            return result

    async def extract_dominant_colors(
        self, image_data: bytes, num_colors: int = 10
    ) -> List[str]:
        """Extract dominant colors from an image."""
        try:
            # Create a temporary file for ColorThief
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(image_data)

            # Use ColorThief to extract dominant colors
            ct = colorthief.ColorThief(temp_path)
            palette = ct.get_palette(color_count=num_colors, quality=10)

            # Convert to hex colors
            hex_colors = [
                "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2]) for rgb in palette
            ]

            # Clean up temporary file
            import os
            os.unlink(temp_path)

            return hex_colors

        except Exception as e:
            logger.exception(f"Error extracting dominant colors: {e}")
            return []

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None