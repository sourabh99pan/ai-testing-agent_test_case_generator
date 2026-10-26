
from pathlib import Path
from src.document_reader import extract_module

pdf_path = Path("documents/OHRM-User-Guide.pdf")

pages = extract_module(pdf_path, "login")

print(f"Pages with text extracted: {len(pages)}")

for page in pages:
    print(f"\n--- PDF page {page['page_number']} ---")
    print(page["text"][:500])
