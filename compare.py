"""
Compare outputs from different readers side by side.
Shows character count, time, token usage, and cost.
"""
import os
import json

OUTPUT_DIR = "outputs"

def compare():
    log_path = os.path.join(OUTPUT_DIR, "results.json")
    if not os.path.exists(log_path):
        print("No results.json found. Run run_all.py first.")
        return

    with open(log_path, "r") as f:
        results = json.load(f)

    # Group by PDF
    pdfs = {}
    for r in results:
        pdf = r["pdf"]
        if pdf not in pdfs:
            pdfs[pdf] = []
        pdfs[pdf].append(r)

    for pdf, entries in sorted(pdfs.items()):
        print(f"\n{'='*80}")
        print(f" {pdf}")
        print(f"{'='*80}")
        print(f"  {'Reader':<30} {'Chars':>8} {'Time':>7} {'In Tokens':>10} {'Out Tokens':>11} {'Cost':>10}")
        print(f"  {'-'*30} {'-'*8} {'-'*7} {'-'*10} {'-'*11} {'-'*10}")

        for r in sorted(entries, key=lambda x: x.get("cost_usd") or 0):
            if "error" in r:
                print(f"  {r['reader']:<30} {'ERROR':>8}   {r['error']}")
                continue

            usage = r.get("usage", {})
            in_tok = usage.get("input_tokens", usage.get("pages", "-"))
            out_tok = usage.get("output_tokens", "-")
            cost = f"${r['cost_usd']:.6f}" if r.get("cost_usd") is not None else "free"

            if usage.get("pages"):
                in_tok = f"{usage['pages']}pg"
                out_tok = "-"

            print(f"  {r['reader']:<30} {r['chars']:>8} {r['time_s']:>6.1f}s {str(in_tok):>10} {str(out_tok):>11} {cost:>10}")

if __name__ == "__main__":
    compare()
