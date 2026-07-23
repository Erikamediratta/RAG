from pypdf import PdfReader

def extract(pdf_path):
    reader=PdfReader(pdf_path)
    full_text=""
    for page in reader.pages:
        full_text=full_text+page.extract_text()+"\n"
    full_text=full_text.replace("\x00","")
    return full_text


