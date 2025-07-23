"""Example script to demonstrate using the Website Scraper MCP Server."""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any

import aiohttp


async def scrape_website(url: str, elements: list = None) -> Dict[str, Any]:
    """Scrape a website using the MCP server."""
    if elements is None:
        elements = ["logos", "colors", "styles"]
    
    # MCP server endpoint
    endpoint = "http://localhost:8000/mcp/invoke"
    
    # Prepare request
    request = {
        "tool": "scrape_website",
        "parameters": {
            "url": url,
            "elements": elements,
        }
    }
    
    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=request) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return {"error": await response.text()}
            
            return await response.json()


async def extract_logo(url: str, selector: str = None) -> Dict[str, Any]:
    """Extract logo from a website using the MCP server."""
    # MCP server endpoint
    endpoint = "http://localhost:8000/mcp/invoke"
    
    # Prepare request
    request = {
        "tool": "extract_logo",
        "parameters": {
            "url": url,
        }
    }
    
    if selector:
        request["parameters"]["selector"] = selector
    
    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=request) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return {"error": await response.text()}
            
            return await response.json()


async def extract_colors(url: str, element_focus: str = None) -> Dict[str, Any]:
    """Extract colors from a website using the MCP server."""
    # MCP server endpoint
    endpoint = "http://localhost:8000/mcp/invoke"
    
    # Prepare request
    request = {
        "tool": "extract_colors",
        "parameters": {
            "url": url,
        }
    }
    
    if element_focus:
        request["parameters"]["element_focus"] = element_focus
    
    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=request) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return {"error": await response.text()}
            
            return await response.json()


async def extract_ui_styles(url: str, component_types: list = None) -> Dict[str, Any]:
    """Extract UI styles from a website using the MCP server."""
    # MCP server endpoint
    endpoint = "http://localhost:8000/mcp/invoke"
    
    # Prepare request
    request = {
        "tool": "extract_ui_styles",
        "parameters": {
            "url": url,
        }
    }
    
    if component_types:
        request["parameters"]["component_types"] = component_types
    
    # Send request
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=request) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                return {"error": await response.text()}
            
            return await response.json()


async def main():
    """Run the example script."""
    parser = argparse.ArgumentParser(description="Website Scraper Example")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--tool", choices=["scrape_website", "extract_logo", "extract_colors", "extract_ui_styles"], 
                        default="scrape_website", help="Tool to use")
    parser.add_argument("--elements", nargs="+", help="Elements to extract (for scrape_website)")
    parser.add_argument("--selector", help="CSS selector (for extract_logo)")
    parser.add_argument("--element-focus", help="Element focus (for extract_colors)")
    parser.add_argument("--component-types", nargs="+", help="Component types (for extract_ui_styles)")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Call appropriate function based on tool
    if args.tool == "scrape_website":
        result = await scrape_website(args.url, args.elements)
    elif args.tool == "extract_logo":
        result = await extract_logo(args.url, args.selector)
    elif args.tool == "extract_colors":
        result = await extract_colors(args.url, args.element_focus)
    elif args.tool == "extract_ui_styles":
        result = await extract_ui_styles(args.url, args.component_types)
    
    # Print or save result
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())