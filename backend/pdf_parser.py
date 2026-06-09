import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    # open the bytes with pdfplumber using io.BytesIO
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            if page.extract_text():
                text += f"--- Page {i + 1} ---\n"
                text += page.extract_text() + "\n"
    if not text:
        raise ValueError("No text could be extracted. The PDF may be a scanned image.")
    return text