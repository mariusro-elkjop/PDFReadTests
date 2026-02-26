"""
Run all PDF readers against input PDFs and save outputs for comparison.
Logs token usage and estimated cost per reader.
"""
import os
import sys
import importlib
import time
import json

from pricing import calculate_cost

INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "outputs"

def get_readers():
    """Discover all reader modules in the readers/ directory."""
    readers = {}
    for filename in sorted(os.listdir("readers")):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"readers.{module_name}")
            if hasattr(module, "read_pdf"):
                readers[module_name] = module.read_pdf
    return readers

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDFs found in {INPUT_DIR}/")
        sys.exit(1)

    readers = get_readers()
    if not readers:
        print("No readers found in readers/")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF(s) and {len(readers)} reader(s)\n")

    all_results = []

    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]

        print(f"--- {pdf_file} ---")
        for reader_name, read_fn in readers.items():
            output_dir = os.path.join(OUTPUT_DIR, reader_name)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{pdf_name}.txt")

            try:
                start = time.time()
                text, usage = read_fn(pdf_path)
                elapsed = time.time() - start

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)

                cost = calculate_cost(reader_name, usage)
                cost_str = f"${cost:.6f}" if cost is not None else "N/A"

                result_entry = {
                    "pdf": pdf_file,
                    "reader": reader_name,
                    "chars": len(text),
                    "time_s": round(elapsed, 2),
                    "usage": usage,
                    "cost_usd": round(cost, 6) if cost is not None else None,
                }
                all_results.append(result_entry)

                usage_str = ""
                if usage.get("input_tokens"):
                    usage_str = f" | in:{usage['input_tokens']} out:{usage['output_tokens']} tokens"
                elif usage.get("pages"):
                    usage_str = f" | {usage['pages']} pages"

                print(f"  {reader_name}: {len(text)} chars in {elapsed:.2f}s | cost: {cost_str}{usage_str}")

            except Exception as e:
                print(f"  {reader_name}: ERROR - {e}")
                all_results.append({
                    "pdf": pdf_file,
                    "reader": reader_name,
                    "error": str(e),
                })

    # Save results log as JSON
    log_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults log saved to {log_path}")

    # Print cost summary
    print("\n=== COST SUMMARY ===")
    totals = {}
    for r in all_results:
        if r.get("cost_usd") is not None:
            name = r["reader"]
            totals[name] = totals.get(name, 0) + r["cost_usd"]
    for name in sorted(totals):
        print(f"  {name}: ${totals[name]:.6f}")
    total = sum(totals.values())
    print(f"  {'TOTAL':}: ${total:.6f}")

    # Generate markdown report
    generate_markdown_report(all_results)

    print("\nDone. Compare results in the outputs/ directory.")


def generate_markdown_report(all_results):
    """Generate a markdown report with a table per PDF showing all readers and costs."""
    # Group by PDF
    pdfs = {}
    for r in all_results:
        pdf = r["pdf"]
        if pdf not in pdfs:
            pdfs[pdf] = []
        pdfs[pdf].append(r)

    lines = []
    lines.append("# PDF Reader Comparison Report\n")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Per-PDF tables
    for pdf_file in sorted(pdfs):
        entries = pdfs[pdf_file]
        lines.append(f"## {pdf_file}\n")
        lines.append("| Reader | Chars | Time (s) | Input Tokens | Output Tokens | Cost (USD) |")
        lines.append("|--------|------:|--------:|-------------:|--------------:|-----------:|")

        for r in sorted(entries, key=lambda x: x.get("cost_usd") or 0):
            if "error" in r:
                lines.append(f"| {r['reader']} | ERROR | - | - | - | - |")
                continue

            usage = r.get("usage", {})
            in_tok = usage.get("input_tokens", "-")
            out_tok = usage.get("output_tokens", "-")
            if usage.get("pages"):
                in_tok = f"{usage['pages']} pages"
                out_tok = "-"

            cost = f"${r['cost_usd']:.6f}" if r.get("cost_usd") is not None else "free"
            lines.append(f"| {r['reader']} | {r['chars']} | {r['time_s']:.1f} | {in_tok} | {out_tok} | {cost} |")

        lines.append("")

    # Cost summary table
    lines.append("## Cost Summary\n")
    lines.append("| Reader | Total Cost (USD) |")
    lines.append("|--------|-----------------:|")

    totals = {}
    for r in all_results:
        if r.get("cost_usd") is not None:
            name = r["reader"]
            totals[name] = totals.get(name, 0) + r["cost_usd"]

    for name in sorted(totals, key=lambda x: totals[x]):
        lines.append(f"| {name} | ${totals[name]:.6f} |")

    grand_total = sum(totals.values())
    lines.append(f"| **TOTAL** | **${grand_total:.6f}** |")
    lines.append("")

    report_path = os.path.join(OUTPUT_DIR, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Markdown report saved to {report_path}")


if __name__ == "__main__":
    run()
