"""
Claude Haiku (via Azure AI Foundry) PDF reader.
Sends PDF as a document to Claude Haiku for text extraction.
"""
import os
import base64
from dotenv import load_dotenv
from anthropic import AnthropicFoundry

load_dotenv()

RESOURCE = os.getenv("AZURE_AI_FOUNDRY_RESOURCE")
KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
MODEL = os.getenv("AZURE_CLAUDE_HAIKU_MODEL", "claude-haiku-4-5")

SYSTEM_PROMPT = (
    "You are a precise document transcription assistant. "
    "Extract ALL text from this PDF exactly as it appears. "
    "Preserve the original structure, formatting, tables, and layout as closely as possible. "
    "Do not summarize or omit anything. Output only the extracted text."
)


def read_pdf(pdf_path: str) -> tuple[str, dict]:
    with open(pdf_path, "rb") as f:
        pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    client = AnthropicFoundry(
        resource=RESOURCE,
        api_key=KEY,
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=16384,
        system=SYSTEM_PROMPT,
        messages=[
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
    )

    text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text, usage
