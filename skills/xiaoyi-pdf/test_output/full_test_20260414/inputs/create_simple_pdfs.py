import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io

base = r'D:\1Codes\celia\Astra\skills\xiaoyi-pdf\test_output\full_test_20260414\inputs'

# Simple 3-page PDF for merge/split/watermark
out1 = os.path.join(base, 'simple_3page.pdf')
writer = __import__('pypdf').PdfWriter()
for i in range(1, 4):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, f"Page {i} of Document A")
    c.showPage()
    c.save()
    buf.seek(0)
    writer.add_page(__import__('pypdf').PdfReader(buf).pages[0])
with open(out1, 'wb') as f:
    writer.write(f)
print(f"Created: {out1}")

# Simple 2-page PDF for merge
out2 = os.path.join(base, 'simple_2page.pdf')
writer = __import__('pypdf').PdfWriter()
for i in range(1, 3):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, f"Page {i} of Document B")
    c.showPage()
    c.save()
    buf.seek(0)
    writer.add_page(__import__('pypdf').PdfReader(buf).pages[0])
with open(out2, 'wb') as f:
    writer.write(f)
print(f"Created: {out2}")

# Table PDF for extraction
out3 = os.path.join(base, 'table_source.pdf')
buf = io.BytesIO()
doc = SimpleDocTemplate(buf, pagesize=letter)
data = [
    ["Product", "Q1 Sales", "Q2 Sales", "Total"],
    ["Widget A", "1200", "1500", "2700"],
    ["Widget B", "800", "950", "1750"],
    ["Widget C", "2000", "2200", "4200"],
]
table = Table(data)
table.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
]))
doc.build([table])
with open(out3, 'wb') as f:
    f.write(buf.getvalue())
print(f"Created: {out3}")
