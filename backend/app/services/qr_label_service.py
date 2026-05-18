"""
QR Label Service - Generates QR codes and PDF label sheets for warehouse locations.

This is a pure utility module with no FastAPI dependencies.
It can be called from any router to generate QR code images or PDF label sheets.

Requirements: 3.1, 3.2, 3.4
"""

import io
from dataclasses import dataclass, field
from typing import List, Optional

import qrcode
from qrcode.image.pil import PilImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@dataclass
class LabelLayout:
    """Configuration for the label grid layout on A4 paper."""

    columns: int = 3
    rows: int = 7
    page_width: float = 210.0  # mm (A4)
    page_height: float = 297.0  # mm (A4)
    margin_top: float = 10.0  # mm
    margin_bottom: float = 10.0  # mm
    margin_left: float = 7.0  # mm
    margin_right: float = 7.0  # mm
    label_padding: float = 2.0  # mm - internal padding within each label
    gap_x: float = 2.0  # mm - horizontal gap between labels
    gap_y: float = 2.0  # mm - vertical gap between labels

    @property
    def labels_per_page(self) -> int:
        return self.columns * self.rows

    @property
    def usable_width(self) -> float:
        """Usable width in mm after margins."""
        return self.page_width - self.margin_left - self.margin_right

    @property
    def usable_height(self) -> float:
        """Usable height in mm after margins."""
        return self.page_height - self.margin_top - self.margin_bottom

    @property
    def label_width(self) -> float:
        """Width of a single label in mm."""
        total_gaps = self.gap_x * (self.columns - 1)
        return (self.usable_width - total_gaps) / self.columns

    @property
    def label_height(self) -> float:
        """Height of a single label in mm."""
        total_gaps = self.gap_y * (self.rows - 1)
        return (self.usable_height - total_gaps) / self.rows


@dataclass
class LocationLabel:
    """Data for a single location label."""

    location_code: str
    description: Optional[str] = None
    parts: Optional[List[str]] = field(default_factory=list)


def generate_qr_code(url: str, box_size: int = 10, border: int = 1) -> bytes:
    """
    Generate a QR code PNG image as bytes for the given URL.

    Args:
        url: The URL to encode in the QR code.
        box_size: Size of each box in the QR code grid (pixels).
        border: Border size in boxes around the QR code.

    Returns:
        PNG image bytes of the QR code.
    """
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version based on data
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def generate_label_pdf(
    locations: List[dict],
    base_url: str,
    layout: Optional[LabelLayout] = None,
) -> bytes:
    """
    Generate a PDF with QR code labels for the given locations.

    Each label contains:
    - QR code encoding the location URL
    - Location code in large bold text
    - Part names in small text (if provided)

    Args:
        locations: List of dicts with keys:
            - location_code (str): The location code (e.g., "A1", "B3-top")
            - description (str, optional): Location description
            - parts (list[str], optional): List of part names at this location
        base_url: Base URL for QR codes, e.g. "https://abparts.oraseas.com/locate/warehouse-uuid"
            The location_code will be appended to form the full URL.
        layout: Optional LabelLayout configuration. Uses sensible defaults if not provided.

    Returns:
        PDF file bytes ready for download/streaming.
    """
    if layout is None:
        layout = LabelLayout()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Convert layout dimensions to points (reportlab uses points)
    page_w = layout.page_width * mm
    page_h = layout.page_height * mm
    margin_left = layout.margin_left * mm
    margin_top = layout.margin_top * mm
    label_w = layout.label_width * mm
    label_h = layout.label_height * mm
    gap_x = layout.gap_x * mm
    gap_y = layout.gap_y * mm
    padding = layout.label_padding * mm

    # Process each location
    label_index = 0
    for loc_data in locations:
        location_code = loc_data.get("location_code", "")
        parts = loc_data.get("parts") or []

        # Start a new page if needed
        if label_index > 0 and label_index % layout.labels_per_page == 0:
            c.showPage()

        # Calculate position on current page
        pos_on_page = label_index % layout.labels_per_page
        col = pos_on_page % layout.columns
        row = pos_on_page // layout.columns

        # Calculate label origin (bottom-left corner)
        # Labels are laid out top-to-bottom, left-to-right
        x = margin_left + col * (label_w + gap_x)
        y = page_h - margin_top - (row + 1) * label_h - row * gap_y

        # Draw label border (light gray dashed line for cutting guide)
        c.saveState()
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setDash(1, 2)
        c.rect(x, y, label_w, label_h, stroke=1, fill=0)
        c.restoreState()

        # Generate QR code for this location
        url = f"{base_url.rstrip('/')}/{location_code}"
        qr_bytes = generate_qr_code(url, box_size=6, border=1)
        qr_image = ImageReader(io.BytesIO(qr_bytes))

        # Layout within the label:
        # Top portion: QR code (centered)
        # Below QR: location code (large bold)
        # Bottom: part names (small text)
        inner_x = x + padding
        inner_y = y + padding
        inner_w = label_w - 2 * padding
        inner_h = label_h - 2 * padding

        # Allocate space: QR gets ~55% of height, text gets the rest
        qr_area_height = inner_h * 0.55
        text_area_height = inner_h * 0.45

        # Draw QR code (square, centered horizontally)
        qr_size = min(qr_area_height, inner_w * 0.85)
        qr_x = inner_x + (inner_w - qr_size) / 2
        qr_y = inner_y + text_area_height  # QR sits above text area

        c.drawImage(
            qr_image,
            qr_x,
            qr_y,
            width=qr_size,
            height=qr_size,
            preserveAspectRatio=True,
        )

        # Draw location code (large bold text, centered)
        code_font_size = min(14, inner_w / (len(location_code) * 0.6))
        code_font_size = max(code_font_size, 8)  # Minimum readable size
        c.setFont("Helvetica-Bold", code_font_size)

        code_y = inner_y + text_area_height - code_font_size - 2
        code_text_width = c.stringWidth(location_code, "Helvetica-Bold", code_font_size)
        code_x = inner_x + (inner_w - code_text_width) / 2
        c.drawString(code_x, code_y, location_code)

        # Draw part names (small text, centered, max 2-3 lines)
        if parts:
            parts_font_size = 6
            c.setFont("Helvetica", parts_font_size)
            # Join parts, truncate if too long
            parts_text = ", ".join(parts)
            max_chars = int(inner_w / (parts_font_size * 0.45))

            # Split into lines if needed
            lines = []
            max_lines = 2
            remaining = parts_text
            for _ in range(max_lines):
                if not remaining:
                    break
                if len(remaining) <= max_chars:
                    lines.append(remaining)
                    remaining = ""
                else:
                    # Find a good break point
                    cut = remaining[:max_chars].rfind(",")
                    if cut == -1:
                        cut = max_chars - 3
                    lines.append(remaining[: cut + 1].strip())
                    remaining = remaining[cut + 1 :].strip()

            if remaining:
                # Add ellipsis to last line
                if lines:
                    lines[-1] = lines[-1].rstrip(",") + "..."

            # Draw lines below the location code
            line_y = code_y - parts_font_size - 4
            for line in lines:
                line_width = c.stringWidth(line, "Helvetica", parts_font_size)
                line_x = inner_x + (inner_w - line_width) / 2
                c.drawString(line_x, line_y, line)
                line_y -= parts_font_size + 1

        label_index += 1

    # Finalize PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
