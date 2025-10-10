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

        doc = converter.convert(file_path)
        text = doc.document.export_to_text() if doc.document else ""
        # Try to get per-page text if possible, else fallback to whole doc
        pages = []
        if hasattr(doc.document, "pages") and hasattr(doc.document.pages, "__iter__"):
            for i, page in enumerate(doc.document.pages):
                page_text = getattr(page, "text", None)
                if page_text is None and hasattr(page, "export_to_text"):
                    page_text = page.export_to_text()
                if page_text is None:
                    # fallback: use full document text
                    page_text = text
                pages.append(
                    PageMeta(
                        index=i + 1,
                        text_length=len(page_text),
                        has_signature_hint="signature" in page_text.lower()
                    )
                )
        else:
            pages = [PageMeta(index=1, text_length=len(text), has_signature_hint="signature" in text.lower())]
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
