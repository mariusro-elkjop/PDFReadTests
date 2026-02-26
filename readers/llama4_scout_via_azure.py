"""
Llama 4 Scout (via Azure AI Foundry) PDF reader.
Converts PDF pages to images and sends to Llama 4 Scout for extraction.
"""
import os
import base64
from openai import AzureOpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF - for converting PDF pages to images

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
DEPLOYMENT = os.getenv("AZURE_LLAMA4_SCOUT_DEPLOYMENT", "Llama-4-Scout-17B-16E-Instruct")

SYSTEM_PROMPT = (
    "You are a precise document transcription assistant. "
    "Extract ALL text from these document page images exactly as it appears. "
    "Preserve the original structure, formatting, tables, and layout as closely as possible. "
    "Do not summarize or omit anything. Output only the extracted text."
)


def _pdf_pages_to_base64_images(pdf_path: str) -> list[str]:
    """Convert each PDF page to a base64-encoded PNG image."""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        images.append(base64.b64encode(img_bytes).decode("utf-8"))
    doc.close()
    return images


def read_pdf(pdf_path: str) -> tuple[str, dict]:
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=KEY,
        api_version="2024-12-01-preview",
    )

    page_images = _pdf_pages_to_base64_images(pdf_path)

    content = []
    for img_b64 in page_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_b64}",
                "detail": "high",
            },
        })
    content.append({
        "type": "text",
        "text": "Extract all text from these document pages.",
    })

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        max_tokens=16384,
    )

    usage = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }
    return response.choices[0].message.content, usage
