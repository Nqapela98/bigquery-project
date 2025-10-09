import logging
from pathlib import Path
from docling.document_converter import DocumentConverter, InputFormat
from models import ParsedDocument, PageMeta
from pdf_ocr_utils import run_pdf_ocr

logger = logging.getLogger(__name__)

class PDFParser:
    """Parses PDFs using Docling with OCR fallback"""

    async def parse(self, job_id: str, file_path: str) -> ParsedDocument:
        filename = Path(file_path).name
        converter = DocumentConverter()

        doc = converter.convert(file_path, format=InputFormat.PDF)
        text = doc.text_content or ""

        pages = [
            PageMeta(index=i + 1, text_length=len(p.text))
            for i, p in enumerate(doc.pages)
        ]

        # OCR fallback if text is too short
        if len(text.strip()) < 200:
            logger.warning(f"[{job_id}] Low text density — running OCR fallback")
            text = await run_pdf_ocr(file_path)
            pages = [PageMeta(index=1, text_length=len(text))]

        # Signature detection
        text_lower = text.lower()
        for p in pages:
            p.has_signature_hint = any(k in text_lower for k in ["signature", "sign", "signed by"])

        return ParsedDocument(
            job_id=job_id,
            filename=filename,
            text=text,
            pages=pages,
            metadata={"parser": "docling+ocr"}
        )
