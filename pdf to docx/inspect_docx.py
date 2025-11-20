from docx import Document

doc = Document('lab2.docx')
for i, section in enumerate(doc.sections):
    print(f"Section {i}: Bottom Margin = {section.bottom_margin.cm} cm, Footer Distance = {section.footer_distance.cm} cm")
