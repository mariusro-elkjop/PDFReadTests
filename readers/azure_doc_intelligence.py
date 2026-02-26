"""
Azure Document Intelligence (formerly Form Recognizer) PDF reader.
Uses the prebuilt-read model for text extraction.
"""
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
KEY = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")


def read_pdf(pdf_path: str) -> str:
    client = DocumentIntelligenceClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY),
    )

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-read",
            body=f,
            content_type="application/octet-stream",
        )

    result = poller.result()
    return result.content
