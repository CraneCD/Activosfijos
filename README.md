# Asset Label Maker

A Streamlit web application for generating PDF labels with barcodes for asset management.

## Features

- 🏷️ Generate PDF labels with barcodes
- 📱 Web-based interface (no desktop installation required)
- 📄 Multiple labels per page (8 labels per 10cm x 10cm page)
- 🔢 Support for multiple asset codes
- 📥 Direct PDF download

## Deployment on Streamlit Cloud

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Click "New app"**
4. **Select your forked repository**
5. **Set the main file path to `app.py`**
6. **Click "Deploy!"**

## Local Development

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Add Asset Codes**: Enter the asset codes you want to generate labels for
2. **Remove Codes**: Click the ❌ button next to any code you want to remove  
3. **Add More Codes**: Click the ➕ button to add additional codes
4. **Generate PDF**: Click the "Generate PDF" button to create your labels
5. **Download**: Click the download button to save the PDF to your computer

## File Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md            # This file
```

## Requirements

- Python 3.8+
- Streamlit
- ReportLab
- Pillow (PIL)

## Label Specifications

- **Page Size**: 10cm x 10cm
- **Labels per Page**: 8 (2 columns x 4 rows)
- **Label Size**: 5cm x 2.5cm each
- **Barcode**: Code128 format
- **Text**: Helvetica Bold, 10pt

