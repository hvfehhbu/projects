from html4docx import HtmlToDocx
import codecs
from docx import Document

docx_filename = "btl.docx"

with codecs.open("btl.html", 'r', 'utf-8') as f:
    html = f.read()

# Create a new document
document = Document()

new_parser = HtmlToDocx()
new_parser.add_html_to_document(html, document)

document.save(docx_filename)

print(f"Successfully converted btl.html to {docx_filename}")
