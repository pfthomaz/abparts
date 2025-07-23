"""Data models for the Website Scraper MCP Server."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field, HttpUrl, validator


class BrowserType(str, Enum):
    """Enum for browser types."""
    
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class ElementType(str, Enum):
    """Enum for element types."""
    
    BUTTON = "button"
    BACKGROUND = "background"
    TEXT = "text"
    HEADER = "header"
    FOOTER = "footer"
    LOGO = "logo"
    HERO = "hero"
    BANNER = "banner"
    NAVIGATION = "navigation"
    FORM = "form"
    CARD = "card"
    TABLE = "table"
    MODAL = "modal"
    UNKNOWN = "unknown"


class ColorCategory(str, Enum):
    """Enum for color categories."""
    
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    BACKGROUND = "background"
    TEXT = "text"
    BORDER = "border"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Enum for component types."""
    
    BUTTON = "button"
    FORM = "form"
    CARD = "card"
    NAVIGATION = "nav"
    TABLE = "table"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    TABS = "tabs"
    ACCORDION = "accordion"
    PAGINATION = "pagination"
    ALERT = "alert"
    BADGE = "badge"
    TOOLTIP = "tooltip"
    PROGRESS = "progress"


class Logo(BaseModel):
    """Model representing an extracted logo."""
    
    url: str
    src: str
    alt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    data: Optional[str] = None  # Base64 encoded image data
    score: Optional[float] = None  # Confidence score


class Color(BaseModel):
    """Model representing an extracted color."""
    
    hex: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[int, int, int]
    category: Optional[str] = None  # primary, secondary, accent, etc.
    element_type: Optional[str] = None  # button, text, background, etc.
    frequency: float  # Percentage of usage


class ColorRelationship(BaseModel):
    """Model representing a relationship between colors."""
    
    type: str  # complementary, analogous, triadic, etc.
    colors: List[Color]


class Typography(BaseModel):
    """Model representing typography information."""
    
    font_family: str
    sizes: List[int]
    weights: List[int]
    line_heights: List[float]
    element_types: List[str]  # heading, paragraph, button, etc.


class ComponentStyle(BaseModel):
    """Model representing a UI component style."""
    
    type: str  # button, form, card, etc.
    css_properties: Dict[str, str]
    examples: Optional[List[str]] = None  # HTML snippets of examples


class UIStyle(BaseModel):
    """Model representing UI styling information."""
    
    typography: List[Typography]
    spacing: Dict[str, List[int]]
    components: List[ComponentStyle]
    frameworks: List[str]
    breakpoints: Dict[str, int]


class ScrapingOptions(BaseModel):
    """Model representing scraping options."""
    
    browser_type: BrowserType = BrowserType.CHROMIUM
    viewport_width: int = 1280
    viewport_height: int = 800
    timeout: int = 30000  # milliseconds
    wait_until: str = "networkidle"  # load, domcontentloaded, networkidle
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    include_images: bool = True
    max_depth: int = 1  # For multi-page scraping
    excluded_elements: List[str] = []
    comparison_urls: List[str] = []  # For side-by-side analysis
    element_focus: Optional[str] = None  # For color extraction
    component_types: List[str] = []  # For UI style extraction
    export_format: str = "json"  # json, csv, html, pdf
    cache_ttl: int = 3600  # seconds


class ScrapingRequest(BaseModel):
    """Model representing a scraping request."""
    
    url: str
    elements: List[str] = ["logos", "colors", "styles"]
    selectors: Optional[Dict[str, str]] = None
    options: Optional[Dict[str, Any]] = None
    
    @validator("elements")
    def validate_elements(cls, v):
        """Validate elements."""
        valid_elements = {"logos", "colors", "styles"}
        if not set(v).issubset(valid_elements):
            invalid = set(v) - valid_elements
            raise ValueError(f"Invalid elements: {invalid}. Valid options are: {valid_elements}")
        return v


class ScrapingResult(BaseModel):
    """Model representing a scraping result."""
    
    url: str
    timestamp: datetime = Field(default_factory=datetime.now)
    logos: Optional[List[Logo]] = None
    colors: Optional[List[Color]] = None
    color_palette: Optional[Dict[str, List[Color]]] = None
    ui_style: Optional[UIStyle] = None
    screenshots: Optional[Dict[str, str]] = None  # Base64 encoded screenshots
    metadata: Optional[Dict[str, str]] = None  # Page metadata
    comparison_results: Optional[Dict[str, Any]] = None  # For side-by-side analysis
    error: Optional[str] = None