---
name: xiaoyi-xlsx
description: "Create, edit, or fix spreadsheet files(.xlsx/.xlsm/.csv/.tsv). Trigger when the deliverable is a spreadsheet — whether from scratch, from other data sources, or modifying an existing file. Includes: formula-driven analysis (VLOOKUP/INDEX+MATCH/SUMIFS), cross-sheet references, charts, conditional formatting, financial models, and professional styling with per-sheet build+validate workflow. Keywords: 图表/可视化/跨表/财务分析/数据分析/对比分析/表格/dashboard/chart/Excel. Do NOT trigger when the primary deliverable is a Word doc, HTML report, standalone script, database pipeline, or Google Sheets API integration."
---

## Excel File Creation: Python + openpyxl/pandas

**✅ REQUIRED Technology Stack for Excel Creation:**
- **Runtime**: Python 3
- **Primary Library**: openpyxl (for Excel file creation, styling, formulas)
- **Data Processing**: pandas (for data manipulation, then export via openpyxl)
- **Execution**: Write code to a `.py` file, then run with `python3 <filename>.py`

**🔧 Execution Environment:**
- Write all Excel generation code to a `.py` script file
- Execute via shell: `python3 <filename>.py`
- Verify output file exists after execution before proceeding

---

## 1. Sheet-by-Sheet Iterative Workflow (Mandatory for Formula Workbooks)

When the workbook involves formulas, references, or calculations, follow this strict per-sheet pipeline. **Never create all sheets first then check — errors cascade.**

**The Cover Page (Section 2) is always the FIRST sheet created.** After the Cover Page passes validation, proceed to data/analysis sheets in order.

For each sheet in the workbook, execute in order:

1. **PLAN** — Design the sheet's structure, data layout, formulas, and cross-sheet references before writing any code.
2. **CREATE** — Write data, formulas, and styles precisely. Preserve original formatting; no arbitrary changes.
3. **SAVE** — Execute `wb.save()` immediately to prevent data loss.
4. **RECALC** — Run `python3 scripts/recalc.py <file>.xlsx` to trigger formula evaluation. Check the returned JSON:
   - `status: success` → proceed to CHECK
   - `status: errors_found` → fix all locations listed in `error_summary` and re-run RECALC before proceeding
5. **CHECK** — Verify every cell: confirm no `#VALUE!`, `#DIV/0!`, `#REF!`, `#NAME?`, `#N/A` errors and no suspicious zero values. Confirm user requirements are met.
6. **NEXT** — Only proceed to the next sheet when the current sheet is fully error-free.

After all sheets pass:
7. **VALIDATE** — Full workbook audit: cross-sheet references, data linkage, formula correctness, and all user requirements satisfied. Also verify the Cover Page's Key Metrics and Sheet Index are accurate and up-to-date with the final workbook contents.
8. **DELIVER** — Only deliver the validated file.

### Recalc Script Output Format
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": { "count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"] }
  }
}
```

### Recheck Rules
- ❌ Never batch-create all sheets then check afterward
- ❌ Never skip the PLAN phase for any sheet
- ❌ Never skip RECALC — openpyxl formulas are strings until recalculated; CHECK without RECALC is blind
- ❌ Never ignore CHECK errors or deliver a file with known issues
- ✅ Must fix all errors and suspicious zeros before moving on
- ✅ Always append "内容由AIGC生成" to the bottom of every sheet (including the Cover Page)


### Progress Reporting

Report progress **between tool calls**, not batched at the end:

| Step | Report Format |
|------|---------------|
| PLAN | `📋 PLAN: [sheet名] — X行数据，Y个公式` |
| CREATE+SAVE | `✅ CREATE+SAVE: [sheet名] — 已创建并保存` |
| RECALC | `🔄 RECALC: 公式数 N，错误数 N` |
| CHECK | `🔍 CHECK: [sheet名] — PASS ✅ / FAIL ❌` |
| Final | `📊 完成！共 N 个工作表，M 个公式，0 错误` |

`save_wb()` prints `✅ Saved output.xlsx | sheet=数据表 | rows=50 | formulas=100` — always read and verify before RECALC.

### Rules
- ❌ Never batch-create all sheets then check afterward
- ❌ Never skip PLAN, RECALC, or CHECK for any sheet
- ❌ Never silently move to next sheet without reporting status
- ✅ Fix all errors before moving on; max 3 RECALC retries per sheet
- ✅ Always append "内容由AIGC生成" to the bottom of every sheet

---

## 2. Cover Page (Mandatory — First Sheet of Every Workbook)

**Every Excel deliverable MUST include a Cover Page as the FIRST sheet.** The Cover Page serves as a professional title page, executive summary, and navigation index for the workbook.

### Cover Page Layout

| Row(s) | Content | Style |
|--------|---------|-------|
| 2–3 | **Report Title** | Large font (18–20pt), Bold, Centered across merged columns A–G |
| 5 | Subtitle / Description | Medium font (12pt), Gray text color |
| 7–15 | **Key Metrics Summary** | Table format with 3–6 highlighted KPIs |
| 17–20 | **Sheet Index** | Table listing every sheet with a short description |
| 22+ | Notes & Instructions | Small font (9–10pt), Gray text color |

### Required Elements
**1. Report Title**
- Clear, descriptive title of the workbook's purpose.
- Merge cells A2:G3 (or wider to match workbook width) and center the title.

**2. Key Metrics Summary**
- Display 3–6 of the most important numbers or findings from the workbook.
- Use formulas referencing the source sheets so values stay in sync (e.g., `=Analysis!B2`).
- Apply the workbook's color theme to highlight key figures.

**3. Sheet Index**
- A navigation table listing every sheet in the workbook:

```
| Sheet Name | Description                        |
|------------|------------------------------------|
| Raw Data   | Original dataset (100 rows)        |
| Analysis   | Sales breakdown by region          |
| Charts     | Visualizations of key trends       |
```

- Update this table during the VALIDATE step (Section 1, step 7) to ensure it matches the final workbook structure.

### Cover Page Styling

- **Background**: Clean white or light gray fill (`#F5F5F5` / `PatternFill('solid', fgColor='F5F5F5')`)
- **Title row height**: 30–40pt for visual prominence
- **Gridlines**: Always hidden on the Cover sheet (`ws.sheet_view.showGridLines = False`)
- **Column width**: Merge cells A–G (minimum) for the title area; set uniform column widths for the metrics and index tables
- **Color scheme**: Match the workbook's overall theme (Pure or Professional Finance — see Section 7)
- **Font**: Use the workbook's consistent professional font (e.g., Arial)

### Cover Page Code Example

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
 
 
def create_cover_page(wb, title, subtitle, metrics, sheet_index, notes=None):
    ws = wb.create_sheet("Cover", 0)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = ws.column_dimensions['H'].width = 4
    for i in range(2, 8):
        ws.column_dimensions[get_column_letter(i)].width = 16
 
    A, M, W = '2B579A', '6B7280', 'FFFFFF'
    CT = Alignment(horizontal='center', vertical='center', wrap_text=True)
    hf = PatternFill('solid', fgColor=A)
    sf = PatternFill('solid', fgColor='E8EEF7')
    dv = Border(bottom=Side(style='thin', color='D1D5DB'))
    hfn = Font(name='Arial', size=10, bold=True, color=W)
 
    def put(row, val, font, merge='B:G', fill=None, h=24):
        l, r = merge.split(':')
        ws.merge_cells(f'{l}{row}:{r}{row}')
        c = ws[f'{l}{row}']
        c.value, c.font, c.alignment = val, font, CT
        if fill:
            for x in (l, r):
                ws[f'{x}{row}'].fill = fill
        ws.row_dimensions[row].height = h
 
    def table(row, sec_title, headers, items, fonts):
        put(row, sec_title, Font(name='Arial', size=11, bold=True, color=A), h=28)
        row += 1
        for mg, hd in zip(['C:D', 'E:F'], headers):
            put(row, hd, hfn, mg, hf, 26)
        for i, (v1, v2) in enumerate(items):
            row += 1
            f = sf if i % 2 == 0 else None
            for mg, v, fn in zip(['C:D', 'E:F'], [v1, v2], fonts):
                put(row, v, fn, mg, f)
        return row
 
    def divider(row):
        ws.row_dimensions[row].height = 8
        row += 1
        for i in range(2, 8):
            ws.cell(row, i).border = dv
        ws.row_dimensions[row].height = 10
        return row
 
    # Accent bar
    for i in range(2, 8):
        ws.cell(1, i).fill = hf
    ws.row_dimensions[1].height = 6
    ws.row_dimensions[2].height = 20
 
    # Title & subtitle
    ws.merge_cells('B3:G4')
    c = ws['B3']
    c.value, c.font, c.alignment = title, Font(name='Arial', size=22, bold=True, color='1F2937'), CT
    ws.row_dimensions[3].height = ws.row_dimensions[4].height = 32
    put(5, subtitle, Font(name='Arial', size=12, color=M), h=24)
    for i in range(2, 8):
        ws.cell(6, i).border = dv
    ws.row_dimensions[6].height = 10
 
    # Metrics table
    row = table(8, 'KEY METRICS', ['Metric', 'Value'],
                [(m['label'], m.get('ref', m['value'])) for m in metrics],
                [Font(name='Arial', size=10, color='1F2937'),
                 Font(name='Arial', size=11, bold=True, color=A)])
 
    row = divider(row + 1)
 
    # Index table
    row = table(row + 2, 'SHEET INDEX', ['Sheet Name', 'Description'],
                [(s['name'], s['desc']) for s in sheet_index],
                [Font(name='Arial', size=10, bold=True, color='1F2937'),
                 Font(name='Arial', size=10, color=M)])
 
    # Notes
    if notes:
        row += 2
        put(row, notes, Font(name='Arial', size=9, italic=True, color='9CA3AF'))
 
    # Footer
    row += 2
    put(row, '内容由AIGC生成', Font(name='Arial', size=8, italic=True, color='C0C0C0'))
 
    ws.print_area = f'A1:H{row + 1}'
    ws.page_setup.orientation = 'portrait'
    ws.page_setup.fitToWidth = ws.page_setup.fitToHeight = 1
    return ws
```

### Cover Page Rules
- ❌ Never deliver a workbook without a Cover Page
- ❌ Never leave Key Metrics as static values when the source data lives in other sheets — use cross-sheet formula references
- ❌ Never leave the Sheet Index out of date — update it in the VALIDATE step
- ✅ Always hide gridlines on the Cover sheet
- ✅ Always place the Cover sheet at index 0 (first position)

---

## 3. Formula-First Policy (Mandatory)

For any analytical task, Excel formulas are the **default and only** first choice. If a formula can do it, use a formula. Python pre-calculation with static values is forbidden.

### ✅ Correct
```python
ws['C2'] = '=A2+B2'
ws['D2'] = '=C2/B2*100'
ws['E2'] = '=SUM(A2:A100)'
```

### ❌ Forbidden
```python
result = value_a + value_b
ws['C2'] = result  # Static value — loses dynamic capability
```

### ❌ Also Forbidden — Hardcoded Constants Inside Formulas
```python
ws['C5'] = '=B5*1.05'      # Magic number — not updateable
```
### ✅ Correct — Assumptions in Dedicated Cells
```python
ws['B6'] = 0.05             # Assumption cell — blue font, labelled
ws['C5'] = '=B5*(1+$B$6)'  # References the assumption cell
```
Place ALL assumptions (growth rates, margins, multiples, etc.) in dedicated cells with blue font. Use cell references in formulas — never hardcode numeric constants directly.

### Exceptions (static values allowed)
- Data from external sources (web search, API, batch_search results)
- True constants that never change
- Formulas that would cause circular references

### Source Annotation for Static Values (Mandatory)
When static values come from external sources, annotate in the adjacent cell:
```
Source: [media/system], [date], [specific reference]
```
Examples:
- `Source: 新华网, 2024-03, 2024年营收数据`
- `Source: batch_search, 2025-07, IDC手机出货量报告`

---

## 4. Formula Construction & Verification

### Pre-Write Checklist
Before writing any formula block, verify:
- [ ] **Column mapping**: Confirm Excel column letters match intended DataFrame columns (DataFrame col 64 ≠ Excel column BL — off-by-one is common)
- [ ] **Row offset**: Excel rows are 1-indexed; DataFrame rows are 0-indexed (DataFrame row 5 = Excel row 6)
- [ ] **NaN handling**: Filter null values with `pd.notna()` before writing to avoid broken formula chains
- [ ] **Division by zero**: Check all denominators before using `/` in formulas; wrap with `IFERROR` when in doubt
- [ ] **Cross-sheet format**: Use `SheetName!$A$2:$C$100` syntax for cross-sheet references

### Test Strategy
- Test formulas on 2–3 sample cells before applying to full range
- Verify all referenced cells exist and contain expected data types
- Include edge cases: zero values, negatives, empty cells

### IFERROR Wrapper (use proactively)
```python
ws['D2'] = '=IFERROR(B2/C2, "-")'
ws['E2'] = '=IFERROR(VLOOKUP(A2,$G$2:$I$50,3,FALSE), "N/A")'
```

### ⚠️ data_only=True Warning
**Never open an existing workbook with `data_only=True` and then save it.**
Doing so permanently replaces all formulas with their last cached values — the formulas are gone with no warning and no recovery.
```python
# DANGER — destroys all formulas on save
wb = load_workbook('file.xlsx', data_only=True)
wb.save('file.xlsx')  # ← All formulas now static values, permanently

# SAFE — preserves formulas
wb = load_workbook('file.xlsx')
```

---

## 5. VLOOKUP / INDEX+MATCH Rules

### Trigger Keywords
Use VLOOKUP (or INDEX/MATCH) when you see: "based on", "from another table", "match against", "lookup", "search", shared keys (product ID, employee ID), master-detail relationships, code-to-name mapping, cross-sheet data linkage.

### Syntax
- Default: `=VLOOKUP(lookup_value, table_array, col_index_num, FALSE)`
- Lookup column must be the leftmost column of `table_array`
- Best practices: use `FALSE` for exact match; lock ranges with `$` (e.g. `$A$2:$D$100`); wrap with `IFERROR`; cross-sheet format: `Sheet2!$A$2:$C$100`
- If lookup column is not leftmost → use `INDEX/MATCH`

### Example
```python
ws['D2'] = '=IFERROR(VLOOKUP(A2,$G$2:$I$50,3,FALSE),"N/A")'
```

---

## 6. Chart Creation Rules

### When to Create Charts
- If the user asks for charts/visuals, you MUST actively create charts instead of waiting for explicit per-table requests.
- When a workbook has multiple prepared datasets/tables, ensure **each prepared dataset has at least one corresponding chart** unless the user explicitly says otherwise.

**Trigger Keywords** — When user mentions ANY of these, you MUST create actual embedded charts:
- "visual", "chart", "graph", "visualization", "visual table", "diagram"
- "show me a chart", "create a chart", "add charts", "with graphs"

### Requirements
- ❌ Never create a "chart data" sheet with instructions for manual chart creation
- ❌ Never tell the user to create charts themselves
- ✅ Use `openpyxl.chart` to create embedded charts in the .xlsx file
- Only generate standalone PNG/JPG if the user explicitly requests it

### Chart Configuration
Read `references/charts.md` for detailed chart type selection, code examples, and configuration patterns.

---

## 7. Visual Style Guide

Two styles are available. Choose based on task type:

| Style | When to Use |
|-------|-------------|
| **Pure** | Default for all non-financial tasks |
| **Professional Finance** | Financial/fiscal analysis only (stocks, GDP, salary, revenue, profit, budget, ROI, public finance, etc.) |

Read `references/styles.md` for complete color palettes, code examples, and conditional formatting rules.

### Key Principles (both styles)
- Hide gridlines: `ws.sheet_view.showGridLines = False`
- Use `openpyxl` for all styling (not pandas)
- Preserve original styles when editing existing files

### Text Color Convention (Mandatory)
| Color | Meaning |
|-------|---------|
| **Blue** | Fixed / input values (including assumption cells) |
| **Black** | Calculated formula cells |
| **Green** | Cross-worksheet references |
| **Red** | External link references |

### Border Style
- Default: no borders (cleaner look)
- Use thin 1px lines for internal model structure
- Use slightly thicker lines (2px) for section dividers
- Only add borders to highlight calculation results or sections

---

## 8. Financial Model Number Formatting (Professional Finance Style Only)

When using Professional Finance style, apply these number format standards:

| Data Type | Format | Notes |
|-----------|--------|-------|
| Years | Text string `"2024"` | Never numeric — avoids thousand-separator display |
| Currency | `$#,##0` | Always specify units in header: `Revenue ($mm)` |
| Zero values | `-` via format `$#,##0;($#,##0);-` | Applies to percentages too |
| Percentages | `0.0%` | One decimal place default |
| Negative numbers | `(123)` parentheses | Never `-123` minus sign |
| Multiples | `0.0x` | For EV/EBITDA, P/E, etc. |

```python
# Apply finance number formats
from openpyxl.styles import numbers

ws['B2'].number_format = '$#,##0'               # currency
ws['C2'].number_format = '0.0%'                 # percentage
ws['D2'].number_format = '$#,##0;($#,##0);-'    # zero as dash
ws['E2'].number_format = '0.0x'                 # multiples
```

---

## 9. Conditional Formatting (Proactive)

Proactively apply conditional formatting to 2–4 key columns per sheet for professional impact.

| Data Type | Format | Rule |
|-----------|--------|------|
| Numeric values | Data Bars | `DataBarRule(start_type='min', end_type='max', color='5A9BD4')` |
| Distribution | Color Scales | `ColorScaleRule(start/end with appropriate colors)` |
| KPIs/Status | Icon Sets | `IconSetRule('3TrafficLights1', type='percent', values=[0,33,67])` |
| Thresholds | Highlight Cells | `CellIsRule(operator='greaterThan', ...)` |

Read `references/styles.md` for full code examples and style-specific combinations.

---

## 10. General Document Processing Strategy

### Incremental Modification (Default)
Load the original/template document; replace, fill, or insert content directly. **Fully preserve** original structure, styles, TOC, cross-references, and multi-level numbering.

> ⚠️ Never open with `data_only=True` when the goal is to preserve or extend formulas — see Section 4 warning.

### New Document
Only use when purely referencing styles. Call `import_styles_from()` to import template styles, then build from scratch.

### Content Cleanup
Remove all instructional text, placeholders, fill-in guides, examples, and `${variable}` patterns — keep only formal business content.

### Complex Structure Documents
Documents with multi-level TOC, cross-references, or batch custom styles **must** use incremental modification. Never recreate from scratch — this breaks structure.

