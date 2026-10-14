"""Phase-3 gate, run by hand: import the real archived submissions and prove nothing identifying
survives into the text that would be sent to a provider.

Usage:
    uv run python -m scripts.verify_import [directory]      # default: ../samples

Why a script and not a test: the archived submissions are real student work and are deliberately not
in the repository, so CI cannot run this. The strongest available check is therefore to push every
file through the exact pipeline the API uses and then run the **egress guard** over the result — if
the guard accepts the text, the text is sendable by construction, which is precisely the phase-3 gate.

Only file names, counts and classes are printed. A removed value is never echoed, not even to show
what went wrong.
"""

import io
import pathlib
import sys
import traceback

import pdfplumber

from app.ingest.extract import extract, extract_zip
from app.ingest.guard import EgressBlocked, assert_sendable
from app.ingest.identity import extract_identity
from app.ingest.redact import redact
from app.ingest.segment import segment

SUPPORTED = {".pdf", ".docx", ".txt", ".zip"}

# Extraction may legitimately differ from a raw page dump by whitespace, but losing a whole block of
# text is a defect: it truncates what the scorers see. This threshold is what caught the table-first
# extractor silently dropping every non-table line on pages that contain a table.
MIN_COVERAGE = 0.90


def _pdf_page_chars(data: bytes) -> int:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        return sum(len(page.extract_text() or "") for page in pdf.pages)


def check(path: pathlib.Path) -> dict:
    data = path.read_bytes()
    if path.suffix.lower() == ".zip":
        documents, errors = extract_zip(path.name, data)
    else:
        documents, errors = [extract(path.name, data)], []

    report: dict = {"file": path.name, "errors": errors, "documents": []}
    page_chars = _pdf_page_chars(data) if path.suffix.lower() == ".pdf" else 0
    for doc in documents:
        result = segment(doc)
        ai = redact(result.ai_output_text)
        analysis = redact(result.student_analysis_text)

        # The gate: would the provider client let this text leave?
        leaks: list[str] = []
        for label, text in (("ai_output", ai.text), ("student_analysis", analysis.text)):
            if not text.strip():
                continue
            try:
                assert_sendable(text)
            except EgressBlocked as blocked:
                leaks.append(f"{label}:{sorted(c.value for c in blocked.classes)}")

        # And independently: does the identifier we know about still appear anywhere?
        identity = extract_identity(doc.filename, doc.text)
        if identity:
            for label, text in (("ai_output", ai.text), ("student_analysis", analysis.text)):
                if identity.casefold() in text.casefold():
                    leaks.append(f"{label}:name_still_present")

        extracted_chars = sum(len(b.text) for b in doc.blocks)
        coverage = extracted_chars / page_chars if page_chars else 1.0
        if page_chars and coverage < MIN_COVERAGE:
            leaks.append(f"text_dropped:{coverage:.0%}_of_page_text_extracted")

        report["documents"].append(
            {
                "filename": doc.filename,
                "format": doc.source_format,
                "blocks": len(doc.blocks),
                "segmentation": result.method,
                "has_ai_output": result.has_ai_output,
                "ai_chars": len(ai.text),
                "analysis_chars": len(analysis.text),
                "removed": {e.cls.value: e.count for e in (*ai.events, *analysis.events)},
                "warnings": [*doc.warnings, *result.warnings],
                "coverage": coverage,
                "leaks": leaks,
            }
        )
    return report


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1] if len(argv) > 1 else pathlib.Path(__file__).resolve().parents[2] / "samples")
    if not root.is_dir():
        print(f"No such directory: {root}")
        return 2

    files = sorted(p for p in root.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not files:
        print(f"No importable files in {root}")
        return 2

    failures = 0
    for path in files:
        try:
            report = check(path)
        except Exception:
            failures += 1
            print(f"\n=== {path.name}\n  CRASHED")
            traceback.print_exc(limit=3)
            continue

        for doc in report["documents"]:
            flag = "LEAK" if doc["leaks"] else "ok"
            if doc["leaks"]:
                failures += 1
            print(
                f"\n=== {doc['filename']}\n"
                f"  format={doc['format']} blocks={doc['blocks']} segmentation={doc['segmentation']} "
                f"ai={doc['ai_chars']}c analysis={doc['analysis_chars']}c  {flag}"
            )
            if doc["removed"]:
                print(f"  removed: {doc['removed']}")
            if doc["warnings"]:
                print(f"  warnings: {doc['warnings']}")
            if doc["leaks"]:
                print(f"  PROBLEM: {doc['leaks']}")
        for member, message in report["errors"]:
            print(f"  zip member failed: {member}: {message}")

    print(f"\n{len(files)} file(s) processed, {failures} problem(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
