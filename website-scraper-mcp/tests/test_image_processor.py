"""Tests for the image processor module."""

import asyncio
import base64
import io
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website_scraper_mcp.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """Test the ImageProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()

    @patch("aiohttp.ClientSession")
    @patch("PIL.Image.open")
    async def test_fetch_and_process_image_http(self, mock_image_open, mock_session):
        """Test fetching and processing an image from HTTP URL."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.read = AsyncMock(return_value=b"image_data")
        
        # Mock session
        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Mock PIL Image
        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 200
        mock_img.mode = "RGB"
        mock_img.save = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Mock BytesIO
        mock_bytes_io = MagicMock()
        mock_bytes_io.getvalue.return_value = b"processed_image_data"
        
        with patch("io.BytesIO", return_value=mock_bytes_io):
            # Call fetch_and_process_image
            result = await self.processor.fetch_and_process_image("https://example.com/image.png")
        
        # Verify session was created with correct headers
        self.assertIn("User-Agent", mock_session_instance.headers)
        
        # Verify get was called with correct URL
        mock_session_instance.get.assert_called_once_with("https://example.com/image.png", timeout=10)
        
        # Verify response was read
        mock_response.read.assert_called_once()
        
        # Verify image was opened
        mock_image_open.assert_called_once()
        
        # Verify image was saved
        mock_img.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result["width"], 100)
        self.assertEqual(result["height"], 200)
        self.assertEqual(result["format"], "jpeg")
        self.assertTrue(result["data"].startswith("data:image/jpeg;base64,"))
        self.assertIsNone(result["error"])

    async def test_process_data_url(self):
        """Test processing a data URL."""
        # Create a simple data URL
        data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
        # Mock PIL Image
        mock_img = MagicMock()
        mock_img.width = 1
        mock_img.height = 1
        
        with patch("PIL.Image.open") as mock_image_open:
            mock_image_open.return_value.__enter__.return_value = mock_img
            
            # Call _process_data_url
            result = await self.processor._process_data_url(data_url)
        
        # Verify result
        self.assertEqual(result["data"], data_url)
        self.assertEqual(result["width"], 1)
        self.assertEqual(result["height"], 1)
        self.assertEqual(result["format"], "png")
        self.assertIsNone(result["error"])

    async def test_process_data_url_invalid(self):
        """Test processing an invalid data URL."""
        # Create an invalid data URL
        data_url = "data:image/png;base64,invalid_base64"
        
        # Call _process_data_url
        result = await self.processor._process_data_url(data_url)
        
        # Verify result
        self.assertIsNotNone(result["error"])
        self.assertIn("Error processing data URL", result["error"])

    @patch("colorthief.ColorThief")
    @patch("tempfile.NamedTemporaryFile")
    async def test_extract_dominant_colors(self, mock_temp_file, mock_color_thief):
        """Test extracting dominant colors from an image."""
        # Mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.png"
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        
        # Mock ColorThief
        mock_ct_instance = MagicMock()
        mock_ct_instance.get_palette.return_value = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        ]
        mock_color_thief.return_value = mock_ct_instance
        
        # Mock os.unlink
        with patch("os.unlink") as mock_unlink:
            # Call extract_dominant_colors
            colors = await self.processor.extract_dominant_colors(b"image_data", num_colors=3)
        
        # Verify temporary file was written
        mock_temp.write.assert_called_once_with(b"image_data")
        
        # Verify ColorThief was created with correct path
        mock_color_thief.assert_called_once_with("/tmp/test.png")
        
        # Verify get_palette was called with correct parameters
        mock_ct_instance.get_palette.assert_called_once_with(color_count=3, quality=10)
        
        # Verify temporary file was deleted
        mock_unlink.assert_called_once_with("/tmp/test.png")
        
        # Verify result
        self.assertEqual(len(colors), 3)
        self.assertEqual(colors[0], "#ff0000")
        self.assertEqual(colors[1], "#00ff00")
        self.assertEqual(colors[2], "#0000ff")

    async def test_close(self):
        """Test closing the HTTP session."""
        # Mock session
        mock_session = AsyncMock()
        self.processor.session = mock_session
        
        # Call close
        await self.processor.close()
        
        # Verify session was closed
        mock_session.close.assert_called_once()
        
        # Verify session was set to None
        self.assertIsNone(self.processor.session)


if __name__ == "__main__":
    # Run tests
    unittest.main()