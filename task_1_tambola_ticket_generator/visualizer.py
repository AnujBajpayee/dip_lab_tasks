"""
Tambola Ticket Visualizers & Export Utilities
=============================================
Provides multi-format rendering for Tambola tickets:
- ASCII box-drawing text format
- GitHub Flavored Markdown tables
- Scalable Vector Graphics (SVG)
- Raster PNG images (via Pillow)
"""

from __future__ import annotations
import os
from typing import List, Optional
from .generator import TambolaTicket, TambolaStrip, validate_ticket

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def ticket_to_ascii(ticket: TambolaTicket, title: Optional[str] = None) -> str:
    """Renders a 3x9 Tambola ticket in a formatted ASCII box-drawing table."""
    t_id = title or ticket.ticket_id or "TAMBOLA TICKET"
    header = f"┌─────────────────────────────────────────────────────┐\n"
    header += f"│ {t_id.center(51)} │\n"
    header += f"├─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┤\n"
    header += f"│  1s │ 10s │ 20s │ 30s │ 40s │ 50s │ 60s │ 70s │ 80s │\n"
    header += f"├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤\n"
    
    rows_str = []
    for r_idx, row in enumerate(ticket.grid):
        cells = []
        for val in row:
            if val == 0:
                cells.append("   ")
            else:
                cells.append(f"{val:2d} ")
        row_line = "│ " + " │ ".join(cells) + " │"
        rows_str.append(row_line)
        if r_idx < 2:
            rows_str.append("├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤")
            
    footer = "\n└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘"
    return header + "\n".join(rows_str) + footer


def ticket_to_markdown(ticket: TambolaTicket) -> str:
    """Renders a Tambola ticket as a GitHub Flavored Markdown table."""
    t_id = ticket.ticket_id or "Tambola Ticket"
    md = [f"### 🎟️ {t_id}\n"]
    md.append("| Col 1 (1-9) | Col 2 (10-19) | Col 3 (20-29) | Col 4 (30-39) | Col 5 (40-49) | Col 6 (50-59) | Col 7 (60-69) | Col 8 (70-79) | Col 9 (80-90) |")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for row in ticket.grid:
        cells = [f"**{val:02d}**" if val > 0 else "—" for val in row]
        md.append("| " + " | ".join(cells) + " |")
        
    return "\n".join(md)


def strip_to_ascii(strip: TambolaStrip) -> str:
    """Renders an entire 6-ticket strip in ASCII format."""
    s_id = strip.strip_id or "FULL TAMBOLA STRIP (1-90)"
    sep = "=" * 55
    res = [f"\n{sep}\n  {s_id.center(51)}\n{sep}\n"]
    for i, t in enumerate(strip.tickets, 1):
        res.append(ticket_to_ascii(t, title=f"TICKET #{i} ({t.ticket_id or ''})"))
        res.append("")
    return "\n".join(res)


def strip_to_markdown(strip: TambolaStrip) -> str:
    """Renders an entire 6-ticket strip in Markdown."""
    s_id = strip.strip_id or "Full Tambola Strip (Numbers 1-90)"
    res = [f"## 🎫 {s_id}\n"]
    for i, t in enumerate(strip.tickets, 1):
        res.append(ticket_to_markdown(t))
        res.append("")
    return "\n".join(res)


def ticket_to_svg(
    ticket: TambolaTicket,
    title: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """Renders a Tambola ticket into a modern SVG vector graphic."""
    t_id = title or ticket.ticket_id or "TAMBOLA TICKET"
    width = 720
    height = 290
    cell_w = 70
    cell_h = 60
    start_x = 45
    start_y = 75

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <defs>',
        '    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0f172a" />',
        '      <stop offset="100%" stop-color="#1e293b" />',
        '    </linearGradient>',
        '    <linearGradient id="cellActive" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#3b82f6" />',
        '      <stop offset="100%" stop-color="#1d4ed8" />',
        '    </linearGradient>',
        '  </defs>',
        f'  <!-- Card Background -->',
        f'  <rect x="15" y="15" width="{width-30}" height="{height-30}" rx="16" fill="url(#cardBg)" stroke="#334155" stroke-width="2"/>',
        f'  <!-- Title -->',
        f'  <text x="{width/2}" y="48" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700" text-anchor="middle" letter-spacing="2">{t_id.upper()}</text>',
    ]

    for r in range(3):
        for c in range(9):
            x = start_x + c * cell_w
            y = start_y + r * cell_h
            val = ticket.grid[r][c]
            
            if val > 0:
                svg_parts.append(
                    f'  <rect x="{x+2}" y="{y+2}" width="{cell_w-4}" height="{cell_h-4}" rx="8" fill="url(#cellActive)" stroke="#60a5fa" stroke-width="1.5"/>'
                )
                svg_parts.append(
                    f'  <text x="{x + cell_w/2}" y="{y + cell_h/2 + 7}" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="800" text-anchor="middle">{val}</text>'
                )
            else:
                svg_parts.append(
                    f'  <rect x="{x+2}" y="{y+2}" width="{cell_w-4}" height="{cell_h-4}" rx="8" fill="#1e293b" fill-opacity="0.6" stroke="#334155" stroke-width="1"/>'
                )
                svg_parts.append(
                    f'  <circle cx="{x + cell_w/2}" cy="{y + cell_h/2}" r="2" fill="#475569" />'
                )

    svg_parts.append('</svg>')
    svg_content = "\n".join(svg_parts)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return svg_content


def ticket_to_png(
    ticket: TambolaTicket,
    output_path: str,
    title: Optional[str] = None
) -> None:
    """Renders a Tambola ticket into a high-resolution PNG image using Pillow."""
    if not HAS_PILLOW:
        raise ImportError("Pillow is required for PNG rendering.")
        
    width = 900
    height = 380
    cell_w = 90
    cell_h = 80
    start_x = 45
    start_y = 100

    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([(15, 15), (width - 15, height - 15)], radius=16, outline=(51, 65, 85), width=3)
    t_id = title or ticket.ticket_id or "TAMBOLA TICKET"
    
    try:
        font_title = ImageFont.load_default(size=24)
        font_cell = ImageFont.load_default(size=28)
    except Exception:
        font_title = ImageFont.load_default()
        font_cell = ImageFont.load_default()

    draw.text((width // 2, 45), t_id.upper(), fill=(248, 250, 252), font=font_title, anchor="mm")

    for r in range(3):
        for c in range(9):
            x = start_x + c * cell_w
            y = start_y + r * cell_h
            val = ticket.grid[r][c]

            box = [(x + 3, y + 3), (x + cell_w - 3, y + cell_h - 3)]
            if val > 0:
                draw.rounded_rectangle(box, radius=10, fill=(37, 99, 235), outline=(96, 165, 250), width=2)
                draw.text(
                    (x + cell_w // 2, y + cell_h // 2),
                    f"{val:02d}",
                    fill=(255, 255, 255),
                    font=font_cell,
                    anchor="mm"
                )
            else:
                draw.rounded_rectangle(box, radius=10, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
                cx, cy = x + cell_w // 2, y + cell_h // 2
                draw.ellipse([(cx - 3, cy - 3), (cx + 3, cy + 3)], fill=(71, 85, 105))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG")
