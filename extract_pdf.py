import fitz
import os

def extract_text(pdf_path, output_file):
    output_file.write(f"--- Extracting from {pdf_path} ---\n")
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            output_file.write(f"--- Page {i+1} ---\n")
            output_file.write(text + "\n")
    except Exception as e:
        output_file.write(f"Error reading {pdf_path}: {e}\n")

base_path = r"c:\Users\Administrator\Documents\Projects\bcnc3.2"
files = ["HW4-Ch03d.pdf", "Gtm_03g_Thev.pdf"]
output_path = r"c:\Users\Administrator\Documents\Projects\extracted_text.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for file in files:
        path = os.path.join(base_path, file)
        extract_text(path, f)
