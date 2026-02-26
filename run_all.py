"""
Run all PDF readers against input PDFs and save outputs for comparison.
"""
import os
import sys
import importlib
import time

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
                text = read_fn(pdf_path)
                elapsed = time.time() - start

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"  {reader_name}: {len(text)} chars in {elapsed:.2f}s -> {output_path}")
            except Exception as e:
                print(f"  {reader_name}: ERROR - {e}")

    print("\nDone. Compare results in the outputs/ directory.")

if __name__ == "__main__":
    run()
