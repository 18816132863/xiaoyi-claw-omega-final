# Visual Styles & Conditional Formatting Reference

## Pure Style

### Core Palette (strictly enforced)

**Base colors (only these allowed):**
- White `#FFFFFF` — main background, content areas
- Black `#000000` — primary titles, body text
- Grey (multiple shades) — structural lines, separators, auxiliary elements, borders

**Accent color:**
- Blue tones only — for emphasis, differentiation, highlighting (vary by lightness/saturation)
- **Forbidden**: green, red, orange, purple, yellow, pink, or any other hue (except region-specific financial indicators)

### Forbidden
- ❌ Green, red, orange, purple, yellow, pink, or other chromatic colors
- ❌ Rainbow or multi-color schemes
- ❌ High-saturation / vibrant colors (except blue tones)
- ❌ Multi-hue gradients

### Python Color Palette
```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Base colors (black, white, grey)
bg_white         = "FFFFFF"   # Main background
bg_light_grey    = "FAFAFA"   # Secondary background
bg_row_alt       = "F5F5F5"   # Alternating row fill
header_black     = "111111"   # Primary title
header_dark_grey = "2D2D2D"   # Section title
text_primary     = "111111"   # Body text
border_grey      = "CCCCCC"   # Borders

# Refined blue accents (sophisticated, muted)
blue_primary     = "0A4D8C"   # Main highlight (deep ocean blue)
blue_secondary   = "3E78B2"   # Secondary accent
blue_light       = "E8F0F8"   # Light background highlight
blue_soft        = "5A9BD4"   # Data bars / conditional format primary

# Example: header styling
header_fill = PatternFill(start_color=header_dark_grey, end_color=header_dark_grey, fill_type="solid")
header_font = Font(color="FFFFFF", bold=True, name="Calibri", size=11)

# Hide gridlines
ws.sheet_view.showGridLines = False
```

---

## Professional Finance Style

Only use when the task explicitly involves financial/fiscal analysis.

### Regional Up/Down Color Convention (Critical)

| Region | Up/Gain | Down/Loss |
|--------|---------|-----------|
| **China (中国大陆)** | **Red** | **Green** |
| **International (all others)** | **Green** | **Red** |

### Python Color Palette
```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

# Base colors
bg_main          = "F7F9FC"   # Main background (very light blue-grey)
text_primary     = "1A1A1A"   # Body text
header_navy      = "0F1C3A"   # Deep navy title
highlight_warm   = "FFF8E1"   # Key metric warm yellow highlight

# Up/Down colors
positive_green   = "2E7D32"   # International up / China down (deep emerald)
negative_red     = "C62828"   # International down / China up (deep brick red)
neutral_yellow   = "FFAB00"   # Neutral warning (amber)

# Example: finance header styling
header_fill = PatternFill(start_color=header_navy, end_color=header_navy, fill_type="solid")
header_font = Font(color="FFFFFF", bold=True, name="Calibri", size=11)
highlight_fill = PatternFill(start_color=highlight_warm, end_color=highlight_warm, fill_type="solid")

# Hide gridlines
ws.sheet_view.showGridLines = False
```

---

## Conditional Formatting (Proactive Application)

Apply to 2–4 key columns per sheet. Keep color meanings consistent throughout.

### Required Imports
```python
from openpyxl.formatting.rule import DataBarRule, ColorScaleRule, IconSetRule, CellIsRule
```

### Data Bars (blue tone)
```python
ws.conditional_formatting.add('C2:C100',
    DataBarRule(start_type='min', end_type='max', color='5A9BD4', showValue=True))
```

### Three-Color Scale (finance: red → yellow → green for international)
```python
ws.conditional_formatting.add('D2:D100',
    ColorScaleRule(
        start_type='min', start_color='C62828',
        mid_type='percentile', mid_value=50, mid_color='FFAB00',
        end_type='max', end_color='2E7D32'))
```

### Icon Sets
```python
ws.conditional_formatting.add('E2:E100',
    IconSetRule('3TrafficLights1', type='percent', values=[0, 33, 67], showValue=True))
```

### Best Practices
- Apply to 2–4 key columns per sheet
- Keep color semantics consistent across the workbook
- Preferred combination: Data Bars + Icon Sets
