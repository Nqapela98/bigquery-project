from pydantic import BaseModel
from typing import List, Dict, Optional

class PageMeta(BaseModel):
    index: int
    text_length: int
    has_signature_hint: bool = False

class ParsedDocument(BaseModel):
    job_id: str
    filename: str
    text: str
    pages: List[PageMeta]
    metadata: Dict[str, str] = {}

class FieldSpec(BaseModel):
    name: str
    description: str
    required: bool = True

class KeyValue(BaseModel):
    key: str
    value: str
    confidence: float = 1.0

class ExtractedFields(BaseModel):
    document_name: Optional[str] = None
    page_count: int
    signature_present: bool
    key_values: List[KeyValue]
