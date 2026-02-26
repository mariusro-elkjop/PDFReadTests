"""Run a single reader and merge results into existing results.json."""
import os
import sys
import time
import json
import importlib
from pricing import calculate_cost

INPUT_DIR = "input_pdfs"

def run(reader_name):
    module = importlib.import_module(f"readers.{reader_name}")
    read_pdf = module.read_pdf

    output_dir = f"outputs/{reader_name}"
    os.makedirs(output_dir, exist_ok=True)

    pdfs = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")])
    results = []

    for pdf_file in pdfs:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        try:
            start = time.time()
            text, usage = read_pdf(pdf_path)
            elapsed = time.time() - start
            with open(os.path.join(output_dir, f"{pdf_name}.txt"), "w") as f:
                f.write(text)
            cost = calculate_cost(reader_name, usage)
            results.append({
                "pdf": pdf_file,
                "reader": reader_name,
                "chars": len(text),
                "time_s": round(elapsed, 2),
                "usage": usage,
                "cost_usd": round(cost, 6) if cost is not None else None,
            })
            cost_str = f"${cost:.6f}" if cost is not None else "N/A"
            print(f"{pdf_file}: {len(text)} chars in {elapsed:.1f}s | cost: {cost_str} | {usage}")
        except Exception as e:
            print(f"{pdf_file}: ERROR - {e}")
            results.append({"pdf": pdf_file, "reader": reader_name, "error": str(e)})

    total = sum(r.get("cost_usd", 0) for r in results)
    print(f"\nTotal cost: ${total:.6f}")

    # Merge into existing results.json
    log_path = "outputs/results.json"
    existing = json.load(open(log_path)) if os.path.exists(log_path) else []
    existing = [r for r in existing if r.get("reader") != reader_name]
    existing.extend(results)
    with open(log_path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"Results merged into {log_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_single_reader.py <reader_name>")
        sys.exit(1)
    run(sys.argv[1])
