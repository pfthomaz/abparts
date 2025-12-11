"""Exporters for the Website Scraper MCP Server."""

import csv
import io
import json
import logging
from typing import Any, Dict, List, Optional

from website_scraper_mcp.models import ScrapingResult

logger = logging.getLogger(__name__)


class ResultExporter:
    """Exports scraping results in different formats."""

    @staticmethod
    def export_json(result: ScrapingResult) -> str:
        """Export result as JSON."""
        return json.dumps(result.dict(), indent=2)

    @staticmethod
    def export_csv(result: ScrapingResult) -> str:
        """Export result as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Type", "Category", "Hex", "RGB", "HSL"])

        # Write colors
        if result.colors:
            for color in result.colors:
                writer.writerow([
                    "Color",
                    color.element_type or "Unknown",
                    color.hex,
                    f"rgb({color.rgb[0]}, {color.rgb[1]}, {color.rgb[2]})",
                    f"hsl({color.hsl[0]}, {color.hsl[1]}%, {color.hsl[2]}%)"
                ])

        # Write logos
        if result.logos:
            for logo in result.logos:
                writer.writerow([
                    "Logo",
                    logo.format,
                    logo.src,
                    f"{logo.width or 'unknown'}x{logo.height or 'unknown'}",
                    logo.alt or "No alt text"
                ])

        # Write typography
        if result.ui_style and result.ui_style.typography:
            for typography in result.ui_style.typography:
                writer.writerow([
                    "Typography",
                    ", ".join(typography.element_types),
                    typography.font_family,
                    f"Sizes: {', '.join(map(str, typography.sizes))}",
                    f"Weights: {', '.join(map(str, typography.weights))}"
                ])

        return output.getvalue()

    @staticmethod
    def export_html(result: ScrapingResult) -> str:
        """Export result as HTML."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Website Analysis: {result.url}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".section { margin-bottom: 30px; }",
            ".color-swatch { display: inline-block; width: 100px; height: 100px; margin: 5px; text-align: center; border-radius: 5px; }",
            ".color-info { padding: 5px; background: rgba(255,255,255,0.8); border-radius: 3px; margin-top: 60px; }",
            ".logo-container { margin: 10px; display: inline-block; }",
            ".logo-image { max-width: 200px; max-height: 100px; border: 1px solid #ddd; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Website Analysis: {result.url}</h1>",
            f"<p>Analysis timestamp: {result.timestamp}</p>"
        ]

        # Add color palette section
        if result.color_palette:
            html.append("<div class='section'>")
            html.append("<h2>Color Palette</h2>")
            
            for category, colors in result.color_palette.items():
                if category != "relationships" and colors:
                    html.append(f"<h3>{category.title()} Colors</h3>")
                    html.append("<div>")
                    
                    for color in colors[:8]:  # Limit to 8 colors per category
                        html.append(f"""
                        <div class='color-swatch' style='background-color: {color.hex};'>
                            <div class='color-info'>{color.hex}</div>
                        </div>
                        """)
                    
                    html.append("</div>")
            
            html.append("</div>")

        # Add logos section
        if result.logos:
            html.append("<div class='section'>")
            html.append("<h2>Logos</h2>")
            
            for logo in result.logos:
                html.append("<div class='logo-container'>")
                if logo.data:
                    html.append(f"<img class='logo-image' src='{logo.data}' alt='{logo.alt or 'Logo'}'>")
                else:
                    html.append(f"<img class='logo-image' src='{logo.src}' alt='{logo.alt or 'Logo'}'>")
                html.append(f"<p>Format: {logo.format}</p>")
                if logo.width and logo.height:
                    html.append(f"<p>Dimensions: {logo.width}x{logo.height}</p>")
                html.append("</div>")
            
            html.append("</div>")

        # Add UI style section
        if result.ui_style:
            html.append("<div class='section'>")
            html.append("<h2>UI Styling</h2>")
            
            # Typography
            if result.ui_style.typography:
                html.append("<h3>Typography</h3>")
                html.append("<table>")
                html.append("<tr><th>Element Type</th><th>Font Family</th><th>Sizes</th><th>Weights</th><th>Line Heights</th></tr>")
                
                for typography in result.ui_style.typography:
                    html.append("<tr>")
                    html.append(f"<td>{', '.join(typography.element_types)}</td>")
                    html.append(f"<td>{typography.font_family}</td>")
                    html.append(f"<td>{', '.join(map(str, typography.sizes))}</td>")
                    html.append(f"<td>{', '.join(map(str, typography.weights))}</td>")
                    html.append(f"<td>{', '.join(map(str, typography.line_heights))}</td>")
                    html.append("</tr>")
                
                html.append("</table>")
            
            # Spacing
            if result.ui_style.spacing:
                html.append("<h3>Spacing</h3>")
                html.append("<table>")
                html.append("<tr><th>Type</th><th>Values (px)</th></tr>")
                
                for spacing_type, values in result.ui_style.spacing.items():
                    html.append("<tr>")
                    html.append(f"<td>{spacing_type}</td>")
                    html.append(f"<td>{', '.join(map(str, values))}</td>")
                    html.append("</tr>")
                
                html.append("</table>")
            
            # Components
            if result.ui_style.components:
                html.append("<h3>Components</h3>")
                
                for component in result.ui_style.components:
                    html.append(f"<h4>{component.type.title()}</h4>")
                    html.append("<table>")
                    html.append("<tr><th>Property</th><th>Value</th></tr>")
                    
                    for prop, value in component.css_properties.items():
                        html.append("<tr>")
                        html.append(f"<td>{prop}</td>")
                        html.append(f"<td>{value}</td>")
                        html.append("</tr>")
                    
                    html.append("</table>")
            
            # Frameworks
            if result.ui_style.frameworks:
                html.append("<h3>Detected Frameworks</h3>")
                html.append("<ul>")
                
                for framework in result.ui_style.frameworks:
                    html.append(f"<li>{framework}</li>")
                
                html.append("</ul>")
            
            # Breakpoints
            if result.ui_style.breakpoints:
                html.append("<h3>Responsive Breakpoints</h3>")
                html.append("<table>")
                html.append("<tr><th>Name</th><th>Width (px)</th></tr>")
                
                for name, width in result.ui_style.breakpoints.items():
                    html.append("<tr>")
                    html.append(f"<td>{name}</td>")
                    html.append(f"<td>{width}</td>")
                    html.append("</tr>")
                
                html.append("</table>")
            
            html.append("</div>")

        # Close HTML
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    @staticmethod
    def export_pdf(result: ScrapingResult) -> bytes:
        """Export result as PDF."""
        try:
            import pdfkit
            
            # Generate HTML first
            html = ResultExporter.export_html(result)
            
            # Convert HTML to PDF
            pdf = pdfkit.from_string(html, False)
            return pdf
        except ImportError:
            logger.warning("pdfkit not installed, falling back to HTML")
            html = ResultExporter.export_html(result)
            return html.encode("utf-8")
        except Exception as e:
            logger.exception(f"Error generating PDF: {e}")
            html = ResultExporter.export_html(result)
            return html.encode("utf-8")