import logging
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path
import easyocr

logger = logging.getLogger(__name__)
reader = easyocr.Reader(["en"], gpu=False)

async def run_pdf_ocr(file_path: str) -> str:
    """OCR fallback for scanned PDFs"""
    text_chunks = []
    with TemporaryDirectory() as tmp:
        pages = convert_from_path(file_path, output_folder=tmp, fmt="jpeg")
        for idx, page in enumerate(pages):
            img_path = f"{tmp}/page_{idx}.jpg"
            page.save(img_path, "JPEG")
            result = reader.readtext(img_path, detail=0, paragraph=True)
            text = "\n".join(result)
            text_chunks.append(text)
            logger.info(f"OCR extracted {len(text)} chars from page {idx + 1}")
    return "\n".join(text_chunks)
