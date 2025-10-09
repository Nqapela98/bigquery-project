import logging
from typing import List
from models import ParsedDocument, FieldSpec, ExtractedFields, KeyValue
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PDFExtractor:
    """Extracts structured information from parsed PDF text."""

    async def extract(self, parsed: ParsedDocument, expected_fields: List[FieldSpec]) -> ExtractedFields:
        prompt = self._build_prompt(parsed.text, expected_fields)
        logger.info(f"[{parsed.job_id}] Running structured extractor")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Extract information from the PDF and return valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )

        data = response.choices[0].message.parsed
        key_values = [
            KeyValue(
                key=f.name,
                value=data.get(f.name, ""),
                confidence=1.0 if data.get(f.name) else 0.5
            )
            for f in expected_fields
        ]

        return ExtractedFields(
            document_name=parsed.filename,
            page_count=len(parsed.pages),
            signature_present=any(p.has_signature_hint for p in parsed.pages),
            key_values=key_values
        )

    def _build_prompt(self, text: str, expected_fields: List[FieldSpec]) -> str:
        fields = "\n".join([f"- {f.name}: {f.description}" for f in expected_fields])
        snippet = text[:7000]  # safety cutoff
        return (
            f"Extract the following fields from this PDF:\n"
            f"{fields}\n\n"
            f"PDF Content:\n{snippet}\n\n"
            f"Return valid JSON with field names as keys."
        )
