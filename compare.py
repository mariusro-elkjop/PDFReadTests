"""
Compare outputs from different readers side by side.
"""
import os

OUTPUT_DIR = "outputs"

def compare():
    reader_dirs = sorted([
        d for d in os.listdir(OUTPUT_DIR)
        if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    ])

    if not reader_dirs:
        print("No output directories found. Run run_all.py first.")
        return

    # Collect all output files across readers
    all_pdfs = set()
    for rd in reader_dirs:
        for f in os.listdir(os.path.join(OUTPUT_DIR, rd)):
            if f.endswith(".txt"):
                all_pdfs.add(f)

    print(f"Readers: {', '.join(reader_dirs)}")
    print(f"PDFs:    {len(all_pdfs)}\n")
    print(f"{'PDF':<30} | " + " | ".join(f"{r:<20}" for r in reader_dirs))
    print("-" * (32 + 23 * len(reader_dirs)))

    for pdf_txt in sorted(all_pdfs):
        row = f"{pdf_txt:<30} | "
        for rd in reader_dirs:
            path = os.path.join(OUTPUT_DIR, rd, pdf_txt)
            if os.path.exists(path):
                size = os.path.getsize(path)
                row += f"{size:>10} bytes       | "
            else:
                row += f"{'MISSING':<20} | "
        print(row)

if __name__ == "__main__":
    compare()
