import io
from pypdf import PdfReader
from PIL import Image
import pytesseract


def extract_text(content: bytes, mime_type: str) -> str:
    if mime_type == "text/plain":
        return content.decode("utf-8")
    if mime_type == "application/pdf":
        return _extract_pdf(content)
    if mime_type in ("image/png", "image/jpeg"):
        return _extract_image_ocr(content)
    raise ValueError(f"Unsupported mime type: {mime_type}")


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_image_ocr(content: bytes) -> str:
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image)
