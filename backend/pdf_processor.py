import pdfplumber
MIN_CHARS_PER_PAGE = 50

def extract_document(path):

    texts = []
    tables = []
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
            tables.extend(page.extract_tables())

    text ="\n".join(texts)
    is_scanned =pages ==0 or len(text.strip()) / pages < MIN_CHARS_PER_PAGE 
    return {"text": text, "tables": tables, "pages": pages, "is_scanned": is_scanned}