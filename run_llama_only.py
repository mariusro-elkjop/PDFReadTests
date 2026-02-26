"""Run Llama 4 Scout only and merge results into existing results.json."""
import os
import time
import json
from readers.mistral_docai_via_azure import read_pdf
READER_NAME = "mistral_docai_via_azure"
from pricing import calculate_cost

INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "outputs/mistral_docai_via_azure"
os.makedirs(OUTPUT_DIR, exist_ok=True)

pdfs = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")])
results = []

for pdf_file in pdfs:
    pdf_path = os.path.join(INPUT_DIR, pdf_file)
    pdf_name = os.path.splitext(pdf_file)[0]
    try:
        start = time.time()
        text, usage = read_pdf(pdf_path)
        elapsed = time.time() - start
        with open(os.path.join(OUTPUT_DIR, f"{pdf_name}.txt"), "w") as f:
            f.write(text)
        cost = calculate_cost("mistral_docai_via_azure", usage)
        results.append({
            "pdf": pdf_file,
            "reader": "mistral_docai_via_azure",
            "chars": len(text),
            "time_s": round(elapsed, 2),
            "usage": usage,
            "cost_usd": round(cost, 6),
        })
        print(f"{pdf_file}: {len(text)} chars in {elapsed:.1f}s | in:{usage['input_tokens']} out:{usage['output_tokens']} | ${cost:.6f}")
    except Exception as e:
        print(f"{pdf_file}: ERROR - {e}")
        results.append({"pdf": pdf_file, "reader": "mistral_docai_via_azure", "error": str(e)})

total = sum(r.get("cost_usd", 0) for r in results)
print(f"\nTotal cost: ${total:.6f}")

# Merge into existing results.json
log_path = "outputs/results.json"
existing = json.load(open(log_path)) if os.path.exists(log_path) else []
existing = [r for r in existing if r.get("reader") != "mistral_docai_via_azure"]
existing.extend(results)
with open(log_path, "w") as f:
    json.dump(existing, f, indent=2)
print("Results merged into outputs/results.json")
