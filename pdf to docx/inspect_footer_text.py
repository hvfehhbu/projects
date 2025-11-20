from docx import Document

doc = Document('lab2.docx')
search_text = "Ho Chi Minh City"

print(f"Searching for '{search_text}' in paragraphs...")
count = 0
for i, p in enumerate(doc.paragraphs):
    if search_text in p.text:
        print(f"Found in paragraph {i}: '{p.text}'")
        count += 1
        if count >= 5: break # Just find the first few instances

if count == 0:
    print("Text not found in body paragraphs.")
