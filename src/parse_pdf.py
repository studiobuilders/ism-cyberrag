import os
import glob
import pypdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a single PDF file using pypdf."""
    reader = pypdf.PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def parse_all_pdfs(data_dir: str) -> list[dict]:
    """
    Parses all ISM PDF files (01-25) in the data directory.

    Returns:
        List of dicts: [{"source_file": str, "title": str, "text": str}, ...]
    """
    pdf_pattern = os.path.join(data_dir, "*.pdf")
    pdf_files = sorted(glob.glob(pdf_pattern))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {data_dir}")

    documents = []
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        title = filename.replace(".pdf", "").strip()
        text = extract_text_from_pdf(pdf_path)
        documents.append({
            "source_file": filename,
            "title": title,
            "text": text,
        })
        print(f"  ✓ {filename} ({len(text):,} chars)")

    print(f"\nParsed {len(documents)} documents, "
          f"{sum(len(d['text']) for d in documents):,} total characters")
    return documents
