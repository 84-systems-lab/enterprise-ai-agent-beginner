"""Inspect real extraction and chunking locally, without AWS credentials."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app/ingestion/runtime")]
from extract_pdf import extract_pages
from extract_text import extract_docx_from_bytes, extract_utf8_text_from_bytes
from chunk_text import chunk_pages

def inspect_document(path, size=800, overlap=100):
    path = Path(path)
    data = path.read_bytes()
    uri = "fixture://" + path.name
    if path.suffix.lower() == ".pdf":
        pages = extract_pages(path, uri)
    elif path.suffix.lower() == ".docx":
        pages = extract_docx_from_bytes(data, path.name, uri)
    elif path.suffix.lower() in {".md", ".txt"}:
        pages = extract_utf8_text_from_bytes(data, path.name, uri)
    else:
        raise ValueError("Use a supported PDF, DOCX, TXT or MD file.")
    chunks = chunk_pages(pages, hashlib.sha256(uri.encode()).hexdigest(),
                         path.suffix[1:], path.name, "fixture-bucket", size, overlap)
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "records": pages, "chunks": chunks}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect_document(args.path, args.size, args.overlap)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as target:
            json.dump(result, target, ensure_ascii=False, indent=2)
    print(json.dumps({"bytes": result["bytes"], "sha256": result["sha256"],
                      "records": len(result["records"]), "chunks": len(result["chunks"]),
                      "first_chunk": result["chunks"][0] if result["chunks"] else None}, indent=2))

if __name__ == "__main__":
    main()
