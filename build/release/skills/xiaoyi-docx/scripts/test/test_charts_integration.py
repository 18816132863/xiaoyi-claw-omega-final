import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx import Document
from docx_utils import setup_chinese_document_styles
from matplotlib_chart_utils import (
    add_column_chart,
    add_bar_chart,
    add_line_chart,
    add_pie_chart,
    add_area_chart,
    add_scatter_chart,
    add_radar_chart,
    add_histogram,
)


def test_create_comprehensive_chart_document():
    doc = Document()
    setup_chinese_document_styles(doc)

    doc.add_paragraph("图表综合测试文档", style="Title")

    add_column_chart(doc, categories=["A", "B", "C"], series=[{"name": "S1", "values": [1, 2, 3]}], title="Column")
    add_bar_chart(doc, categories=["X", "Y", "Z"], series=[{"name": "S1", "values": [3, 2, 1]}], title="Bar")
    add_line_chart(doc, categories=["1", "2", "3"], series=[{"name": "S1", "values": [1, 3, 2]}], title="Line")
    add_pie_chart(doc, categories=["A", "B", "C"], series=[{"name": "S1", "values": [30, 40, 30]}], title="Pie")
    add_area_chart(doc, categories=["Q1", "Q2"], series=[{"name": "S1", "values": [4, 7]}], title="Area")
    add_scatter_chart(
        doc,
        series=[
            {"name": "S1", "values": [(1, 3), (2, 5), (3, 2)]},
        ],
        title="Scatter",
    )
    add_radar_chart(doc, categories=["A", "B", "C"], series=[{"name": "S1", "values": [3, 4, 5]}], title="Radar")
    add_histogram(doc, data=[1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5, title="Histogram")

    out_path = os.path.join(tempfile.gettempdir(), "test_all_charts.docx")
    doc.save(out_path)

    import zipfile
    with zipfile.ZipFile(out_path, "r") as zf:
        media_files = [n for n in zf.namelist() if "media" in n]

    # Expect at least 8 media files for 8 charts
    assert len(media_files) >= 8, f"Expected >=8 media files, got {len(media_files)}"
