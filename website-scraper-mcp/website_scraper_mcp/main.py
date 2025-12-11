"""Main entry point for the Website Scraper MCP Server."""

import argparse
import asyncio
import base64
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

import fastmcp
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from website_scraper_mcp.extractors import (
    ColorExtractor,
    LogoExtractor,
    UIStyleExtractor,
)
from website_scraper_mcp.exporters import ResultExporter
from website_scraper_mcp.image_processor import ImageProcessor
from website_scraper_mcp.browser_automation import BrowserAutomationEngine
from website_scraper_mcp.models import (
    Color,
    ComponentStyle,
    Logo,
    ScrapingRequest,
    ScrapingResult,
    Typography,
    UIStyle,
)
from website_scraper_mcp.scraper import ScrapingOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("website_scraper_mcp")


class WebScraperMCPServer:
    """MCP server for website scraping."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.app = FastAPI(title="Website Scraper MCP Server")
        self.image_processor = ImageProcessor()
        self.browser_engine = BrowserAutomationEngine()
        self.logo_extractor = LogoExtractor()
        self.color_extractor = ColorExtractor()
        self.ui_style_extractor = UIStyleExtractor()
        self.orchestrator = ScrapingOrchestrator()

    def register_tools(self) -> List[Dict[str, Any]]:
        """Register the MCP tools with Kiro."""
        return [
            {
                "name": "scrape_website",
                "description": "Scrape a website to extract visual elements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to scrape",
                        },
                        "elements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of elements to extract (logos, colors, styles)",
                        },
                        "selectors": {
                            "type": "object",
                            "description": "Optional CSS selectors to target specific elements",
                        },
                        "export_format": {
                            "type": "string",
                            "description": "Optional export format (json, csv, html, pdf)",
                            "enum": ["json", "csv", "html", "pdf"],
                        },
                        "options": {
                            "type": "object",
                            "description": "Optional additional options for extraction",
                            "properties": {
                                "browser_type": {
                                    "type": "string",
                                    "description": "Browser type to use (chromium, firefox, webkit)",
                                    "enum": ["chromium", "firefox", "webkit"],
                                },
                                "viewport_width": {
                                    "type": "integer",
                                    "description": "Viewport width in pixels",
                                },
                                "viewport_height": {
                                    "type": "integer",
                                    "description": "Viewport height in pixels",
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in milliseconds",
                                },
                                "wait_until": {
                                    "type": "string",
                                    "description": "When to consider navigation complete",
                                    "enum": ["load", "domcontentloaded", "networkidle"],
                                },
                                "user_agent": {
                                    "type": "string",
                                    "description": "Custom user agent string",
                                },
                                "proxy": {
                                    "type": "string",
                                    "description": "Proxy server URL",
                                },
                                "include_images": {
                                    "type": "boolean",
                                    "description": "Whether to include images in color extraction",
                                },
                                "element_focus": {
                                    "type": "string",
                                    "description": "Element type to focus on for color extraction",
                                    "enum": ["buttons", "backgrounds", "text"],
                                },
                                "component_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Component types to focus on for UI style extraction",
                                },
                                "comparison_urls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "URLs to compare with the main URL",
                                },
                                "excluded_elements": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "CSS selectors for elements to exclude",
                                },
                                "cache_ttl": {
                                    "type": "integer",
                                    "description": "Cache time-to-live in seconds",
                                },
                            },
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_logo",
                "description": "Extract only the logo from a website",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to scrape",
                        },
                        "selector": {
                            "type": "string",
                            "description": "Optional CSS selector for the logo",
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_colors",
                "description": "Extract color palette from a website",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to scrape",
                        },
                        "element_focus": {
                            "type": "string",
                            "description": "Optional element type to focus on (buttons, backgrounds, text)",
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_ui_styles",
                "description": "Extract UI styling information from a website",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to scrape",
                        },
                        "component_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of component types to focus on",
                        },
                    },
                    "required": ["url"],
                },
            },
        ]

    async def handle_request(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        logger.info(f"Handling request for tool: {tool_name} with parameters: {parameters}")
        
        try:
            # Validate common parameters
            if "url" not in parameters:
                return {"error": "Missing required parameter: url"}
            
            url = parameters.get("url")
            if not isinstance(url, str) or not url:
                return {"error": "Invalid URL parameter: URL must be a non-empty string"}
            
            # Handle specific tools
            if tool_name == "scrape_website":
                return await self._handle_scrape_website(parameters)
            elif tool_name == "extract_logo":
                return await self._handle_extract_logo(parameters)
            elif tool_name == "extract_colors":
                return await self._handle_extract_colors(parameters)
            elif tool_name == "extract_ui_styles":
                return await self._handle_extract_ui_styles(parameters)
            else:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}. Available tools: scrape_website, extract_logo, extract_colors, extract_ui_styles"}
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {e}")
            return {"error": str(e), "type": "validation_error"}
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error handling request: {e}")
            return {
                "error": f"An unexpected error occurred: {str(e)}",
                "type": "server_error",
                "details": str(e.__class__.__name__)
            }

    async def _handle_scrape_website(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scrape_website tool requests."""
        url = parameters.get("url")
        elements = parameters.get("elements", ["logos", "colors", "styles"])
        selectors = parameters.get("selectors", {})
        options = parameters.get("options", {})
        export_format = parameters.get("export_format", "json")
        
        # Validate elements parameter
        valid_elements = ["logos", "colors", "styles"]
        if not isinstance(elements, list):
            return {"error": "Invalid elements parameter: must be a list"}
        
        # Filter out invalid elements
        invalid_elements = [e for e in elements if e not in valid_elements]
        if invalid_elements:
            logger.warning(f"Invalid elements requested: {invalid_elements}")
            elements = [e for e in elements if e in valid_elements]
            if not elements:
                return {"error": f"No valid elements specified. Valid options are: {', '.join(valid_elements)}"}
        
        # Validate selectors parameter
        if not isinstance(selectors, dict):
            return {"error": "Invalid selectors parameter: must be a dictionary"}
        
        # Validate export format
        valid_formats = ["json", "csv", "html", "pdf"]
        if export_format not in valid_formats:
            logger.warning(f"Invalid export format: {export_format}")
            export_format = "json"
        
        # Create request and process
        request = ScrapingRequest(
            url=url,
            elements=elements,
            selectors=selectors,
            options=options,
        )
        
        logger.info(f"Processing scrape_website request for {url} with elements: {elements}")
        result = await self.orchestrator.scrape(request)
        
        # Check for errors
        if result.error:
            return {"error": result.error}
        
        # Handle export format if specified
        if export_format and export_format != "json":
            logger.info(f"Exporting result in {export_format} format")
            try:
                if export_format == "csv":
                    csv_data = ResultExporter.export_csv(result)
                    return {
                        "result": result.dict(exclude_none=True),
                        "export": {
                            "format": "csv",
                            "data": csv_data
                        }
                    }
                elif export_format == "html":
                    html_data = ResultExporter.export_html(result)
                    return {
                        "result": result.dict(exclude_none=True),
                        "export": {
                            "format": "html",
                            "data": html_data
                        }
                    }
                elif export_format == "pdf":
                    pdf_data = ResultExporter.export_pdf(result)
                    return {
                        "result": result.dict(exclude_none=True),
                        "export": {
                            "format": "pdf",
                            "data": base64.b64encode(pdf_data).decode("utf-8")
                        }
                    }
            except Exception as e:
                logger.exception(f"Error exporting result to {export_format}: {e}")
                # Fall back to JSON if export fails
                return result.dict(exclude_none=True)
        
        return result.dict(exclude_none=True)

    async def _handle_extract_logo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle extract_logo tool requests."""
        url = parameters.get("url")
        selector = parameters.get("selector")
        
        # Validate selector parameter if provided
        if selector is not None and not isinstance(selector, str):
            return {"error": "Invalid selector parameter: must be a string"}
        
        request = ScrapingRequest(
            url=url,
            elements=["logos"],
            selectors={"logo": selector} if selector else {},
        )
        
        logger.info(f"Processing extract_logo request for {url}")
        result = await self.orchestrator.scrape(request)
        
        # Check for errors
        if result.error:
            return {"error": result.error}
        
        if not result.logos:
            return {
                "error": "No logos found",
                "details": "The system could not identify any logos on the provided website. Try providing a CSS selector for the logo element."
            }
        
        return {"logos": result.logos}

    async def _handle_extract_colors(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle extract_colors tool requests."""
        url = parameters.get("url")
        element_focus = parameters.get("element_focus")
        
        # Validate element_focus parameter if provided
        valid_focuses = ["buttons", "backgrounds", "text"]
        if element_focus is not None:
            if not isinstance(element_focus, str):
                return {"error": "Invalid element_focus parameter: must be a string"}
            if element_focus not in valid_focuses:
                return {"error": f"Invalid element_focus: '{element_focus}'. Valid options are: {', '.join(valid_focuses)}"}
        
        request = ScrapingRequest(
            url=url,
            elements=["colors"],
            options={"element_focus": element_focus} if element_focus else {},
        )
        
        logger.info(f"Processing extract_colors request for {url}")
        result = await self.orchestrator.scrape(request)
        
        # Check for errors
        if result.error:
            return {"error": result.error}
        
        if not result.colors:
            return {
                "error": "No colors found",
                "details": "The system could not extract any colors from the provided website."
            }
        
        return {
            "colors": result.colors,
            "color_palette": result.color_palette,
        }

    async def _handle_extract_ui_styles(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle extract_ui_styles tool requests."""
        url = parameters.get("url")
        component_types = parameters.get("component_types", [])
        
        # Validate component_types parameter
        valid_components = ["button", "form", "card", "nav", "table", "modal"]
        if not isinstance(component_types, list):
            return {"error": "Invalid component_types parameter: must be a list"}
        
        # Filter out invalid component types
        if component_types:
            invalid_components = [c for c in component_types if c not in valid_components]
            if invalid_components:
                logger.warning(f"Invalid component types requested: {invalid_components}")
                component_types = [c for c in component_types if c in valid_components]
        
        request = ScrapingRequest(
            url=url,
            elements=["styles"],
            options={"component_types": component_types} if component_types else {},
        )
        
        logger.info(f"Processing extract_ui_styles request for {url}")
        result = await self.orchestrator.scrape(request)
        
        # Check for errors
        if result.error:
            return {"error": result.error}
        
        if not result.ui_style:
            return {
                "error": "No UI styles found",
                "details": "The system could not extract any UI styling information from the provided website."
            }
        
        return {"ui_style": result.ui_style}


    async def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        if hasattr(self, "image_processor") and self.image_processor:
            await self.image_processor.close()


def main() -> None:
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Website Scraper MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", default="info", help="Logging level")
    
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    
    # Create MCP server
    server = WebScraperMCPServer()
    
    # Register with FastMCP
    fastmcp.register_mcp_server(server.app, server)
    
    # Register shutdown event
    @server.app.on_event("shutdown")
    async def shutdown_event():
        await server.cleanup()
    
    # Run server
    uvicorn.run(server.app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()