import asyncio
from pdf_parser import PDFParser
from pdf_extractor import PDFExtractor
from models import FieldSpec

async def main():
    parser = PDFParser()
    extractor = PDFExtractor()

    job_id = "pdf_test_001"
    file_path = "SERVICE AGREEMENT.pdf"  # ← replace with your PDF path

    parsed = await parser.parse(job_id, file_path)

    expected = [
        FieldSpec(name="contract_number", description="Unique identifier of the contract"),
        FieldSpec(name="client_name", description="Name of the client company"),
        FieldSpec(name="effective_date", description="Date the contract becomes active"),
        FieldSpec(name="expiry_date", description="Date when the contract ends"),
        FieldSpec(name="total_contract_value", description="Total Rand amount stated in the contract"),
]


    extracted = await extractor.extract(parsed, expected)
    print(extracted.model_dump_json(indent=2))

    print("\n=== Extracted Fields ===")
    for kv in extracted.key_values:
        print(f"{kv.key}: {kv.value} (confidence {kv.confidence})")

if __name__ == "__main__":
    asyncio.run(main())
