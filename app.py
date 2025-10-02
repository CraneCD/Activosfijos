import streamlit as st
import io
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import cm
import base64

# Configuration
LABEL_SIZE_CM = 10
LABEL_AREA_WIDTH_CM = 5
LABEL_AREA_HEIGHT_CM = 2.5

def create_pdf(codes):
    """Create PDF with asset labels"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(LABEL_SIZE_CM*cm, LABEL_SIZE_CM*cm))
    
    labels_per_row = int(LABEL_SIZE_CM // LABEL_AREA_WIDTH_CM)  # 2
    labels_per_col = int(LABEL_SIZE_CM // LABEL_AREA_HEIGHT_CM) # 4
    labels_per_page = labels_per_row * labels_per_col           # 8
    
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

def draw_label(c, code, label_x, label_y):
    """Draw a single label with barcode and text"""
    label_w, label_h = LABEL_AREA_WIDTH_CM*cm, LABEL_AREA_HEIGHT_CM*cm
    
    # Draw barcode (squat, wide)
    barcode_height = min(label_h * 0.35, 0.7*cm)
    barcode = code128.Code128(code, barHeight=barcode_height, barWidth=0.045*cm)
    barcode_w = barcode.width
    barcode_x = label_x + (label_w - barcode_w) / 2
    barcode_y = label_y + label_h * 0.4  # Position barcode in upper part
    
    barcode.drawOn(c, barcode_x, barcode_y)
    
    # Draw code text at the bottom of the label area
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(label_x + label_w/2, label_y + 0.18*cm, code)

def main():
    st.set_page_config(
        page_title="Asset Label Maker",
        page_icon="🏷️",
        layout="centered"
    )
    
    st.title("🏷️ Asset Label Maker")
    st.markdown("Generate PDF labels with barcodes for your assets")
    
    # Input section
    st.header("Asset Codes")
    
    # Initialize session state for dynamic inputs
    if 'codes' not in st.session_state:
        st.session_state.codes = ['']
    
    # Display input fields
    for i, code in enumerate(st.session_state.codes):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.session_state.codes[i] = st.text_input(
                f"Asset Code {i+1}", 
                value=code, 
                key=f"code_{i}",
                placeholder="Enter asset code..."
            )
        with col2:
            if st.button("❌", key=f"remove_{i}", help="Remove this code"):
                st.session_state.codes.pop(i)
                st.rerun()
    
    # Add new code button
    if st.button("➕ Add New Code"):
        st.session_state.codes.append('')
        st.rerun()
    
    # Filter out empty codes
    valid_codes = [code.strip() for code in st.session_state.codes if code.strip()]
    
    st.markdown("---")
    
    # Generate PDF section
    if valid_codes:
        st.success(f"Ready to generate PDF with {len(valid_codes)} asset codes")
        
        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_buffer = create_pdf(valid_codes)
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"asset_labels_{len(valid_codes)}_items.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("PDF generated successfully!")
                    
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    else:
        st.warning("Please enter at least one asset code to generate the PDF")
    
    # Instructions
    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("""
    1. **Add Asset Codes**: Enter the asset codes you want to generate labels for
    2. **Remove Codes**: Click the ❌ button next to any code you want to remove
    3. **Add More Codes**: Click the ➕ button to add additional codes
    4. **Generate PDF**: Click the "Generate PDF" button to create your labels
    5. **Download**: Click the download button to save the PDF to your computer
    
    Each label will contain:
    - A barcode for easy scanning
    - The asset code text
    - Proper spacing for standard label sheets
    """)

if __name__ == "__main__":
    main()

