from flask import Flask, request, render_template
import pytesseract
from PIL import Image
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set path to Tesseract executable (update if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_table_from_image(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    data = data.dropna().reset_index(drop=True)
    rows = []

    for _, line_df in data.groupby("line_num"):
        line_text = [word for word in line_df["text"].tolist() if word.strip()]
        if line_text:
            rows.append(line_text)

    if not rows:
        return None

    df = pd.DataFrame(rows)
    return df.to_html(index=False, header=False, border=1)

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = None
    table_html = None
    image_path = None

    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('index.html', extracted_text="No file part")

        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', extracted_text="No selected file")

        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext == '.pdf':
                pages = convert_from_path(filepath, dpi=300)
                text_chunks = []
                table_chunks = []

                for i, page in enumerate(pages):
                    page_path = os.path.join(UPLOAD_FOLDER, f"page_{i}.png")
                    page.save(page_path, 'PNG')
                    img = cv2.imread(page_path)
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        text = pytesseract.image_to_string(thresh)
                        text_chunks.append(text)
                        table_html_chunk = extract_table_from_image(thresh)
                        if table_html_chunk:
                            table_chunks.append(table_html_chunk)

                extracted_text = "\n\n".join(text_chunks)
                table_html = "<br><br>".join(table_chunks)
                image_path = None

            else:
                img_cv = cv2.imread(filepath)
                if img_cv is None:
                    return render_template('index.html', extracted_text="Failed to read image file")

                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 3)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                processed_path = os.path.join(UPLOAD_FOLDER, "processed.png")
                cv2.imwrite(processed_path, thresh)

                extracted_text = pytesseract.image_to_string(Image.open(processed_path))
                table_html = extract_table_from_image(thresh)
                image_path = f"/{filepath.replace('\\', '/')}"

    return render_template('index.html', extracted_text=extracted_text, image_path=image_path, table_html=table_html)

if __name__ == '__main__':
    app.run(debug=True)
