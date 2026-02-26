import { readFileSync } from "node:fs";
import { extractText, getDocumentProxy } from "unpdf";

const pdfPath = process.argv[2];
if (!pdfPath) {
  console.error("Usage: node unpdf_extract.mjs <pdf_path>");
  process.exit(1);
}

const buffer = readFileSync(pdfPath);
const pdf = await getDocumentProxy(new Uint8Array(buffer));
const { text } = await extractText(pdf, { mergePages: true });

process.stdout.write(text);
