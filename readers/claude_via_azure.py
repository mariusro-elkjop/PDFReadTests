"""
Claude (via Azure AI Foundry) PDF reader.
Sends PDF pages as images to Claude for text extraction.
"""
import os
import base64
from anthropic import AnthropicBedrock
from openai import AzureOpenAI
from dotenv import load_dotenv
import httpx

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
MODEL = os.getenv("AZURE_CLAUDE_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = (
    "You are a precise document transcription assistant. "
    "Extract ALL text from this PDF exactly as it appears. "
    "Preserve the original structure, formatting, tables, and layout as closely as possible. "
    "Do not summarize or omit anything. Output only the extracted text."
)


def read_pdf(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    # Use Anthropic Messages API via Azure AI Foundry
    client = httpx.Client()
    response = client.post(
        f"{ENDPOINT}/anthropic/v1/messages",
        headers={
            "api-key": KEY,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": MODEL,
            "max_tokens": 16384,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Extract all text from this PDF.",
                        },
                    ],
                }
            ],
        },
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()

    return "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    )
