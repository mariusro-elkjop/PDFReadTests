"""
Mistral Document AI (via Azure AI Foundry) PDF reader.
Uses the dedicated OCR processor for text extraction.
"""
import os
import base64
from dotenv import load_dotenv
import httpx

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
DEPLOYMENT = os.getenv("AZURE_MISTRAL_DOCAI_DEPLOYMENT", "mistral-document-ai-2505")


def read_pdf(pdf_path: str) -> tuple[str, dict]:
    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    data_uri = f"data:application/pdf;base64,{pdf_b64}"

    client = httpx.Client()
    response = client.post(
        f"{ENDPOINT}/providers/mistral/azure/ocr",
        headers={
            "Authorization": f"Bearer {KEY}",
            "content-type": "application/json",
        },
        json={
            "model": DEPLOYMENT,
            "document": {
                "type": "document_url",
                "document_url": data_uri,
            },
        },
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()

    pages = data.get("pages", [])
    text = "\n\n".join(page.get("markdown", "") for page in pages)

    return text, {"pages": len(pages)}
