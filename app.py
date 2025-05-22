# app.py
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import cm
from PIL import Image
import io
import cairosvg
import os

LOGO_FILENAME = "Logo.svg"
LABEL_SIZE_CM = 10
LABEL_AREA_WIDTH_CM = 5
LABEL_AREA_HEIGHT_CM = 2.5

def create_pdf(codes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(LABEL_SIZE_CM*cm, LABEL_SIZE_CM*cm))
    labels_per_row = int(LABEL_SIZE_CM // LABEL_AREA_WIDTH_CM)
    labels_per_col = int(LABEL_SIZE_CM // LABEL_AREA_HEIGHT_CM)
    labels_per_page = labels_per_row * labels_per_col

    for i, code in enumerate(codes):
        page_index = i // labels_per_page
        pos_in_page = i % labels_per_page
        row = pos_in_page // labels_per_row
        col = pos_in_page % labels_per_row
        x = col * LABEL_AREA_WIDTH_CM * cm
        y = LABEL_SIZE_CM * cm - (row + 1) * LABEL_AREA_HEIGHT_CM * cm
        draw_label(c, code, x, y)
        if (i + 1) % labels_per_page == 0 and (i + 1) < len(codes):
            c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def draw_label(c, code, x, y):
    label_w, label_h = LABEL_AREA_WIDTH_CM*cm, LABEL_AREA_HEIGHT_CM*cm
    y_cursor = y + label_h
    if os.path.exists(LOGO_FILENAME):
        png_bytes = cairosvg.svg2png(url=LOGO_FILENAME, output_width=int(label_w), output_height=int(label_h * 0.45))
        logo = Image.open(io.BytesIO(png_bytes))
        logo_path = "_tmp_logo.png"
        logo.save(logo_path)
        c.drawImage(logo_path, x + (label_w - logo.width) / 2, y_cursor - logo.height, width=logo.width, height=logo.height, mask='auto')
        os.remove(logo_path)
        y_cursor -= logo.height + 0.08 * cm
    else:
        y_cursor -= 0.5 * cm

    barcode = code128.Code128(code, barHeight=min(label_h * 0.35, 0.7*cm), barWidth=0.045*cm)
    barcode.drawOn(c, x + (label_w - barcode.width) / 2, y_cursor - barcode.height)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + label_w / 2, y + 0.18 * cm, code)

# Streamlit Interface
st.title("Asset Label PDF Generator")
codes_input = st.text_area("Enter one code per line:")
if st.button("Generate PDF"):
    codes = [c.strip() for c in codes_input.splitlines() if c.strip()]
    if not codes:
        st.error("Please enter at least one code.")
    else:
        pdf_bytes = create_pdf(codes)
        st.download_button("Download PDF", pdf_bytes, file_name="labels.pdf", mime="application/pdf")
