"""
Pricing per 1M tokens (USD) for each model.
Update these when prices change.
"""

# (input_price_per_1M_tokens, output_price_per_1M_tokens)
MODEL_PRICING = {
    "azure_doc_intelligence": {
        "type": "per_page",
        "price_per_page": 0.01,  # $0.01 per page (prebuilt-read)
    },
    "claude_via_azure": {
        "type": "per_token",
        "input_per_1m": 3.00,   # Claude Sonnet 4.5
        "output_per_1m": 15.00,
    },
    "claude_haiku_via_azure": {
        "type": "per_token",
        "input_per_1m": 0.80,   # Claude Haiku 4.5
        "output_per_1m": 4.00,
    },
    "gpt4o_via_azure": {
        "type": "per_token",
        "input_per_1m": 2.50,   # GPT-4o
        "output_per_1m": 10.00,
    },
    "gpt4o_mini_via_azure": {
        "type": "per_token",
        "input_per_1m": 0.15,   # GPT-4o-mini
        "output_per_1m": 0.60,
    },
    "llama4_scout_via_azure": {
        "type": "per_token",
        "input_per_1m": 0.08,   # Llama 4 Scout 17B 16E
        "output_per_1m": 0.30,
    },
    "mistral_docai_via_azure": {
        "type": "per_page",
        "price_per_page": 0.002,  # Mistral Document AI ~$2/1000 pages
    },
    "unpdf_reader": {
        "type": "free",
    },
}


def calculate_cost(reader_name: str, usage: dict) -> float | None:
    """Calculate cost in USD from usage metadata."""
    pricing = MODEL_PRICING.get(reader_name)
    if not pricing:
        return None

    if pricing["type"] == "free":
        return 0.0

    if pricing["type"] == "per_page":
        pages = usage.get("pages", 0)
        return pages * pricing["price_per_page"]

    if pricing["type"] == "per_token":
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cost = (
            (input_tokens / 1_000_000) * pricing["input_per_1m"]
            + (output_tokens / 1_000_000) * pricing["output_per_1m"]
        )
        return cost

    return None
