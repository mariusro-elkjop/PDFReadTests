"""
unpdf (Node.js) PDF reader.
Calls a small Node.js script to extract text using the unpdf library.
"""
import os
import subprocess

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "unpdf_extract.mjs")


def read_pdf(pdf_path: str) -> tuple[str, dict]:
    abs_pdf_path = os.path.abspath(pdf_path)
    abs_script_path = os.path.abspath(SCRIPT_PATH)

    result = subprocess.run(
        ["node", abs_script_path, abs_pdf_path],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"unpdf script failed: {result.stderr}")

    return result.stdout, {}
