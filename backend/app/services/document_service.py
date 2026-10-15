from pathlib import Path
from pypdf import PdfReader


def extract_document(path: Path) -> list[dict]:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": i, "text": text})
        return pages

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return [{"page": None, "text": text}]

    raise ValueError("Unsupported file type. Use PDF, TXT or MD.")
