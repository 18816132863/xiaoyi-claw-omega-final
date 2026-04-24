import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

out_path = r'D:\1Codes\celia\Astra\skills\xiaoyi-pdf\test_output\full_test_20260414\inputs\form_input.pdf'
c = canvas.Canvas(out_path, pagesize=letter)
c.drawString(100, 750, "Test Form")

# Text fields
c.acroForm.textfield(name='FirstName', tooltip='First Name', x=100, y=700, borderStyle='solid', width=200)
c.acroForm.textfield(name='LastName', tooltip='Last Name', x=100, y=660, borderStyle='solid', width=200)

# Checkbox
c.acroForm.checkbox(name='Agree', tooltip='I Agree', x=100, y=620, buttonStyle='check')

c.save()
print(f"Created: {out_path}")
