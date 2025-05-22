import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import cm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import io
import os

LOGO_FILENAME = "Logo.svg"
LABEL_SIZE_CM = 10
LABEL_AREA_WIDTH_CM = 5
LABEL_AREA_HEIGHT_CM = 2.5

def create_pdf(codes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(LABEL_SIZE_CM * cm, LABEL_SIZE_CM * cm))

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
    label_w = LABEL_AREA_WIDTH_CM * cm
    label_h = LABEL_AREA_HEIGHT_CM * cm
    y_cursor = y + label_h

    # Draw SVG logo
    if os.path.exists(LOGO_FILENAME):
        drawing = svg2rlg(LOGO_FILENAME)
        if drawing:
            logo_width = label_w * 0.95
            scale = logo_width / drawing.width
            drawing.scale(scale, scale)
            renderPDF.draw(drawing, c, x + (label_w - drawing.width * scale) / 2, y_cursor - drawing.height * scale)
            y_cursor -= drawing.height * scale + 0.08 * cm
    else:
        y_cursor -= 0.5 * cm

    # Draw barcode
    barcode_height = min(label_h * 0.35, 0.7 * cm)
    barcode = code128.Code128(code, barHeight=barcode_height, barWidth=0.045 * cm)
    barcode.drawOn(c, x + (label_w - barcode.width) / 2, y_cursor - barcode_height)

    # Draw text
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + label_w / 2, y + 0.18 * cm, code)

# Streamlit UI
st.title("Asset Label PDF Generator")

codes_input = st.text_area("Enter one code per line:")
if st.button("Generate PDF"):
    codes = [code.strip() for code in codes_input.splitlines() if code.strip()]
    if not codes:
        st.error("Please enter at least one valid code.")
    else:
        pdf_file = create_pdf(codes)
        st.success("PDF generated successfully!")
        st.download_button("Download PDF", pdf_file, file_name="labels.pdf", mime="application/pdf")
