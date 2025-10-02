import streamlit as st
import io
import os
import cairosvg
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import cm
import base64

# Configuration
LOGO_FILENAME = "Logo.svg"
LABEL_SIZE_CM = 10
LABEL_AREA_WIDTH_CM = 5
LABEL_AREA_HEIGHT_CM = 2.5

def resource_path(relative_path):
    """ Get absolute path to resource """
    return os.path.join(os.path.abspath("."), relative_path)

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
    """Draw a single label with logo, barcode, and text"""
    label_w, label_h = LABEL_AREA_WIDTH_CM*cm, LABEL_AREA_HEIGHT_CM*cm
    
    # Draw logo at the top of the label area
    y_cursor = label_y + label_h
    logo_path = resource_path(LOGO_FILENAME)
    
    if os.path.exists(logo_path):
        if logo_path.lower().endswith('.svg'):
            max_logo_w = label_w * 0.95
            max_logo_h = label_h * 0.45
            png_bytes = cairosvg.svg2png(url=logo_path, output_width=int(max_logo_w), output_height=int(max_logo_h), dpi=300)
            logo = Image.open(io.BytesIO(png_bytes))
        else:
            logo = Image.open(logo_path)
            max_logo_w = label_w * 0.95
            max_logo_h = label_h * 0.45
            logo.thumbnail((int(max_logo_w), int(max_logo_h)), Image.LANCZOS)
        
        logo_path_temp = "_tmp_logo.png"
        logo.save(logo_path_temp)
        logo_x = label_x + (label_w - logo.width) / 2
        logo_y = y_cursor - logo.height
        c.drawImage(logo_path_temp, logo_x, logo_y, width=logo.width, height=logo.height, mask='auto')
        os.remove(logo_path_temp)
        y_cursor = logo_y - 0.08*cm  # Small gap after logo
    else:
        y_cursor -= 0.5*cm
    
    # Draw barcode (squat, wide)
    barcode_height = min(label_h * 0.35, 0.7*cm)
    barcode = code128.Code128(code, barHeight=barcode_height, barWidth=0.045*cm)
    barcode_w = barcode.width
    barcode_x = label_x + (label_w - barcode_w) / 2
    barcode_y = y_cursor - barcode_height
    barcode.drawOn(c, barcode_x, barcode_y)
    y_cursor = barcode_y - 0.08*cm  # Small gap after barcode
    
    # Draw code text at the bottom of the label area
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(label_x + label_w/2, label_y + 0.18*cm, code)

def main():
    st.set_page_config(
        page_title="Asset Label Maker",
        page_icon="🏷️",
        layout="wide"
    )
    
    st.title("🏷️ Asset Label Maker")
    st.markdown("Generate PDF labels for your fixed assets with barcodes and logos.")
    
    # Sidebar for input
    with st.sidebar:
        st.header("📝 Asset Codes")
        st.markdown("Enter the asset codes you want to generate labels for:")
        
        # Initialize session state for codes
        if 'codes' not in st.session_state:
            st.session_state.codes = ['']
        
        # Display code input fields
        for i, code in enumerate(st.session_state.codes):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.codes[i] = st.text_input(
                    f"Code {i+1}", 
                    value=code, 
                    key=f"code_{i}",
                    placeholder="Enter asset code"
                )
            with col2:
                if len(st.session_state.codes) > 1:
                    if st.button("🗑️", key=f"delete_{i}", help="Delete this code"):
                        st.session_state.codes.pop(i)
                        st.rerun()
        
        # Add new code button
        if st.button("➕ Add Code", use_container_width=True):
            st.session_state.codes.append('')
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 Current Codes")
        valid_codes = [code.strip() for code in st.session_state.codes if code.strip()]
        
        if valid_codes:
            st.success(f"✅ {len(valid_codes)} codes ready for generation")
            for i, code in enumerate(valid_codes, 1):
                st.write(f"{i}. {code}")
        else:
            st.warning("⚠️ Please enter at least one asset code")
    
    with col2:
        st.header("⚙️ Settings")
        st.info("Labels will be generated with:")
        st.write("• Company logo")
        st.write("• Barcode (Code128)")
        st.write("• Asset code text")
        st.write("• 10cm x 10cm page size")
        st.write("• 2.5cm x 5cm label area")
    
    # Generate PDF button
    if valid_codes:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📄 Generate PDF Labels", use_container_width=True, type="primary"):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_buffer = create_pdf(valid_codes)
                        
                        # Create download button
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"asset_labels_{len(valid_codes)}_items.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success(f"✅ PDF generated successfully with {len(valid_codes)} labels!")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")
    else:
        st.info("👆 Add some asset codes in the sidebar to get started!")

if __name__ == "__main__":
    main()
