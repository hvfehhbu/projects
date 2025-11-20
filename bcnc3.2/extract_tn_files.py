import fitz
import os

def extract_text(pdf_path, output_file):
    output_file.write(f"\n\n--- Extracting from {os.path.basename(pdf_path)} ---\n")
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            output_file.write(f"--- Page {i+1} ---\n")
            output_file.write(text + "\n")
    except Exception as e:
        output_file.write(f"Error reading {pdf_path}: {e}\n")

base_path = r"c:\Users\Administrator\Documents\Projects\gtm_tn"
files = ["tn2.pdf", "THIẾT BỊ -  MÔN HỌC TNGTM-HK251.pdf"]
output_path = r"c:\Users\Administrator\Documents\Projects\tn_content.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for file in files:
        path = os.path.join(base_path, file)
        extract_text(path, f)
print(f"Extraction complete to {output_path}")
