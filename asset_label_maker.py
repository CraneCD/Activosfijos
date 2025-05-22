import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import cm
import os
import io
import cairosvg
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

LOGO_FILENAME = resource_path("Logo.svg")
LABEL_SIZE_CM = 10
LABEL_AREA_WIDTH_CM = 5
LABEL_AREA_HEIGHT_CM = 2.5

class AssetLabelMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Label Maker")
        self.code_entries = []
        self.setup_gui()

    def setup_gui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        self.entries_frame = tk.Frame(frame)
        self.entries_frame.pack()

        self.add_code_entry()

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Agregar código", command=self.add_code_entry).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Eliminar código", command=self.remove_code_entry).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Generar PDF", command=self.generate_pdf).pack(pady=10)

    def add_code_entry(self):
        entry = tk.Entry(self.entries_frame, width=20)
        entry.pack(pady=2)
        self.code_entries.append(entry)

    def remove_code_entry(self):
        if len(self.code_entries) > 1:
            entry = self.code_entries.pop()
            entry.destroy()

    def generate_pdf(self):
        codes = [e.get().strip() for e in self.code_entries if e.get().strip()]
        if not codes:
            messagebox.showerror("Error", "Por favor ingrese al menos un código.")
            return
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
        if not pdf_path:
            return
        try:
            self.create_pdf(pdf_path, codes)
            messagebox.showinfo("Éxito", f"PDF creado: {pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_pdf(self, pdf_path, codes):
        c = canvas.Canvas(pdf_path, pagesize=(LABEL_SIZE_CM*cm, LABEL_SIZE_CM*cm))
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
            self.draw_label(c, code, x, y)
            if (i + 1) % labels_per_page == 0 and (i + 1) < len(codes):
                c.showPage()
        c.save()

    def draw_label(self, c, code, label_x, label_y):
        label_w, label_h = LABEL_AREA_WIDTH_CM*cm, LABEL_AREA_HEIGHT_CM*cm
        # Draw logo at the top of the label area
        y_cursor = label_y + label_h
        if os.path.exists(LOGO_FILENAME):
            if LOGO_FILENAME.lower().endswith('.svg'):
                max_logo_w = label_w * 0.95
                max_logo_h = label_h * 0.45
                png_bytes = cairosvg.svg2png(url=LOGO_FILENAME, output_width=int(max_logo_w), output_height=int(max_logo_h), dpi=300)
                logo = Image.open(io.BytesIO(png_bytes))
            else:
                logo = Image.open(LOGO_FILENAME)
                max_logo_w = label_w * 0.95
                max_logo_h = label_h * 0.45
                logo.thumbnail((int(max_logo_w), int(max_logo_h)), Image.LANCZOS)
            logo_path = "_tmp_logo.png"
            logo.save(logo_path)
            logo_x = label_x + (label_w - logo.width) / 2
            logo_y = y_cursor - logo.height
            c.drawImage(logo_path, logo_x, logo_y, width=logo.width, height=logo.height, mask='auto')
            os.remove(logo_path)
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
    root = tk.Tk()
    app = AssetLabelMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main() 