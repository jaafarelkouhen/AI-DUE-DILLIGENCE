import pdfplumber
MIN_CHARS_PER_PAGE = 50

def extract_text_from_pdf(path):

    texts = []
    tables = []
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
            tables.append(page.extract_table() )

    text ="\n".join(texts)
    is_scanmed =pages ==0 or len(text.strip()) / pages < MIN_CHARS_PER_PAGE 
    return {"text": text, "tables": tables, "pages": pages, "is_scanned": is_scanned}