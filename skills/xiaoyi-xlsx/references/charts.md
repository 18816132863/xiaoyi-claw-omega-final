# Chart Creation Reference for openpyxl

## Required Imports

```python
from openpyxl.chart import BarChart, LineChart, PieChart, AreaChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.effect import EffectList
from openpyxl.utils import get_column_letter
```

---

## Hard Rules

- **MUST** create real chart objects and embed them into the worksheet — never create a separate "chart data" sheet with manual instructions.
- **MUST NOT** tell the user to create the chart themselves.
- **MUST NOT** claim "chart added" without actually calling `ws.add_chart(...)`.
- **MUST** set: title, axis labels (except PieChart), data range, category range, and an explicit anchor cell (e.g., `"E2"`).
- **MUST** set `chart.shape = 4` to ensure a standard rectangular aspect ratio.
- **MUST** use the multi-chart layout system below when placing more than one chart on a single sheet — charts must never overlap.

---

## Multi-Chart Layout System (CRITICAL)

When a sheet contains multiple charts, you **MUST** calculate non-overlapping anchor positions. Use this standard layout:

### Standard Chart Dimensions

Each chart occupies approximately **8 columns wide × 15 rows tall** in the worksheet grid. Use these constants:

```python
CHART_WIDTH_COLS = 8    # columns a chart spans
CHART_HEIGHT_ROWS = 15  # rows a chart spans
CHART_GAP_ROWS = 1      # vertical gap between charts
CHART_GAP_COLS = 1      # horizontal gap between charts
```

### Layout Strategy: Choose ONE

**Option A — Vertical Stack (DEFAULT, preferred for ≤4 charts):**
Place charts in a single column, stacked top to bottom.

```python
def get_chart_anchor_vertical(chart_index, start_col="E", start_row=2):
    """Return anchor cell for the Nth chart (0-based) in a vertical stack."""
    row = start_row + chart_index * (CHART_HEIGHT_ROWS + CHART_GAP_ROWS)
    return f"{start_col}{row}"

# Example: 3 charts → "E2", "E18", "E34"
```

**Option B — Grid Layout (use for 5+ charts):**
Place charts in a 2-column grid, wrapping to the next row after every 2 charts.

```python
def get_chart_anchor_grid(chart_index, start_col_num=5, start_row=2, cols_per_row=2):
    """Return anchor cell for the Nth chart (0-based) in a grid layout."""
    grid_row = chart_index // cols_per_row
    grid_col = chart_index % cols_per_row
    row = start_row + grid_row * (CHART_HEIGHT_ROWS + CHART_GAP_ROWS)
    col_num = start_col_num + grid_col * (CHART_WIDTH_COLS + CHART_GAP_COLS)
    return f"{get_column_letter(col_num)}{row}"

# Example: 4 charts → "E2", "N2", "E18", "N18"
```

### Start Column Rule

The `start_col` must be at least **1 column to the right** of the data's last column, so charts never sit on top of data cells:

```python
start_col_num = ws.max_column + 2   # leave a 1-col gap after data
start_col = get_column_letter(start_col_num)
```

### Full Multi-Chart Example

```python
# --- Layout setup ---
CHART_WIDTH_COLS = 8
CHART_HEIGHT_ROWS = 15
CHART_GAP_ROWS = 1
start_col = get_column_letter(ws.max_column + 2)
start_row = 2

charts_config = [
    {"type": "bar",  "title": "Sales by Category",   "y_title": "Revenue ($)",  "x_title": "Category"},
    {"type": "line", "title": "Monthly Trend",        "y_title": "Value",        "x_title": "Month"},
    {"type": "pie",  "title": "Market Share"},
]

for i, cfg in enumerate(charts_config):
    # 1. Create chart
    if cfg["type"] == "bar":
        chart = BarChart(); chart.type = "col"
    elif cfg["type"] == "line":
        chart = LineChart()
    elif cfg["type"] == "pie":
        chart = PieChart()

    chart.title = cfg["title"]
    chart.style = 10
    chart.shape = 4

    if cfg["type"] != "pie":
        chart.y_axis.title = cfg.get("y_title", "")
        chart.x_axis.title = cfg.get("x_title", "")

    # 2. Data & categories (adjust ranges per chart)
    data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
    cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)

    # 3. Calculate non-overlapping anchor
    anchor_row = start_row + i * (CHART_HEIGHT_ROWS + CHART_GAP_ROWS)
    anchor = f"{start_col}{anchor_row}"

    # 4. Embed
    ws.add_chart(chart, anchor)
```

---

## Chart Type Selection

| Data Scenario | Chart Type | Key Config |
|---|---|---|
| Category comparison | `BarChart()` | `type="col"` (vertical) or `type="bar"` (horizontal) |
| Trend / time series | `LineChart()` | `style=10`, add marker points |
| Composition / proportion (≤6 slices) | `PieChart()` | No axes — set title + category labels only |
| Cumulative trend composition | `AreaChart()` | `grouping="standard"` |
| Project timeline | `BarChart()` (Gantt) | `type="bar"`, `grouping="stacked"`, `overlap=100` |

---

## Common Configuration Pattern

Every chart follows the same four steps. Adapt the ranges, titles, and anchor cell to your actual data.

```python
# 1. Create chart & set metadata
chart = BarChart()                         # or LineChart(), PieChart(), etc.
chart.title = "Descriptive Title"
chart.style = 10
chart.shape = 4                            # standard rectangle
chart.y_axis.title = "Y-Axis Label"        # omit for PieChart
chart.x_axis.title = "X-Axis Label"        # omit for PieChart

# 2. Define data range (values — include header row for series name)
data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row, max_col=ws.max_column)
chart.add_data(data_ref, titles_from_data=True)

# 3. Define category range (labels — skip header row)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.set_categories(cats_ref)

# 4. Embed at a specific cell (use layout system for multiple charts!)
ws.add_chart(chart, "E2")
```

---

## Chart-Specific Examples

### Bar / Column Chart

```python
chart = BarChart()
chart.type = "col"                         # "col" = vertical columns, "bar" = horizontal bars
chart.style = 10
chart.shape = 4
chart.title = "Sales by Category"
chart.y_axis.title = "Revenue ($)"
chart.x_axis.title = "Category"

data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws.add_chart(chart, "E2")
```

### Line Chart

```python
chart = LineChart()
chart.title = "Monthly Trend"
chart.style = 10
chart.shape = 4
chart.y_axis.title = "Value"
chart.x_axis.title = "Month"

data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row, max_col=ws.max_column)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws.add_chart(chart, "E2")
```

### Pie Chart

```python
pie = PieChart()
pie.title = "Market Share"
pie.shape = 4

data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
labels_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
pie.add_data(data_ref, titles_from_data=True)
pie.set_categories(labels_ref)

# Optional: show percentage labels
pie.dataLabels = DataLabelList()
pie.dataLabels.showPercent = True

ws.add_chart(pie, "E2")
```

### Area Chart

```python
chart = AreaChart()
chart.grouping = "standard"
chart.title = "Cumulative Revenue by Region"
chart.style = 10
chart.shape = 4
chart.y_axis.title = "Revenue ($)"
chart.x_axis.title = "Quarter"

data_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row, max_col=ws.max_column)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws.add_chart(chart, "E2")
```

### Gantt Chart (Stacked Bar Trick)

Data layout: Column A = task name, Column B = start offset (days from baseline), Column C = duration (days).

```python
chart = BarChart()
chart.type = "bar"
chart.title = "Project Gantt Chart"
chart.shape = 4
chart.y_axis.title = "Tasks"
chart.x_axis.title = "Timeline (days)"
chart.grouping = "stacked"
chart.overlap = 100

# Series 1 = invisible baseline offset; Series 2 = visible duration bar
start_ref = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
dur_ref   = Reference(ws, min_col=3, min_row=1, max_row=ws.max_row)
cats_ref  = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

chart.add_data(start_ref, titles_from_data=True)
chart.add_data(dur_ref,   titles_from_data=True)
chart.set_categories(cats_ref)

# Make the first series (offset) fully invisible
s0 = chart.series[0]
s0.graphicalProperties = GraphicalProperties()
s0.graphicalProperties.noFill = True
s0.graphicalProperties.line = LineProperties()
s0.graphicalProperties.line.noFill = True
s0.graphicalProperties.effectLst = EffectList()

chart.legend = None
ws.add_chart(chart, "E2")
```

---

## Quick Checklist Before Finishing

- [ ] `chart.title` is set and descriptive
- [ ] `chart.shape = 4` is set
- [ ] Axis titles are set (skip for PieChart)
- [ ] `add_data(ref, titles_from_data=True)` uses correct range including header
- [ ] `set_categories(ref)` uses correct range excluding header
- [ ] `ws.add_chart(chart, "CELL")` is called with an explicit anchor cell
- [ ] No orphan "chart data" sheets — chart is embedded in the relevant data sheet
- [ ] **Multiple charts on one sheet use calculated anchors — no two charts share the same anchor or overlapping region**
- [ ] Start column is at least `ws.max_column + 2` so charts don't cover data cells