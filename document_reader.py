from pathlib import Path
import shutil

from pypdf import PdfReader


DOCUMENTS_DIR = Path("documents")


def save_uploaded_pdf(uploaded_file) -> Path:
    """
    Save an uploaded PDF file into the documents folder.
    """

    DOCUMENTS_DIR.mkdir(exist_ok=True)

    file_path = DOCUMENTS_DIR / uploaded_file.name

    with open(file_path, "wb") as file:
        shutil.copyfileobj(uploaded_file, file)

    return file_path


def list_saved_pdfs() -> list[str]:
    """
    Return a list of saved PDF file names.
    """

    DOCUMENTS_DIR.mkdir(exist_ok=True)

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    return [pdf.name for pdf in pdf_files]


def extract_text_from_pdf_file(pdf_name: str) -> str:
    """
    Extract text from one saved PDF file.
    """

    pdf_path = DOCUMENTS_DIR / pdf_name

    reader = PdfReader(str(pdf_path))

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text += f"\n\n--- Page {page_number} ---\n"
            text += page_text

    return text.strip()