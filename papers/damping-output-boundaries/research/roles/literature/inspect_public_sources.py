"""Read-only inspection of explicitly selected public primary-source PDFs.

Full PDFs, text, and renderings stay in ignored local-cache/. Only provenance
metadata is versioned. Network errors are recorded without access workarounds.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from urllib.request import urlopen

from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "local-cache"
SOURCES = {
    "L001-Richiedei2022": (
        "https://iris.univr.it/retrieve/46bbe105-6514-4eba-9877-e8d007960b69/s11831-021-09583-w.pdf",
        [0, 2, 3],
    ),
    "L002-Bonk-notes": (
        "https://www.math.ucla.edu/~mbonk/complana.pdf", [0, 107, 110]
    ),
    "L003-Skudrzyk": (
        "https://www.ioa.org.uk/system/files/publications/EJ%20SKUDRZYK%20UNDERSTANDING%20THE%20DYNAMIC%20BEHAVIOR%20OF%20COMPLEX%20VIBRATORS.pdf",
        [],
    ),
    "L004-DeDomenico-REC2021": (
        "https://rec2021.unime.it/papers/REC2021-67.pdf", []
    ),
}


def inspect(item):
    source_id, (url, pages) = item
    pdf_path = CACHE / (source_id + ".pdf")
    record = {"id": source_id, "requested_url": url,
              "checked_at_utc": datetime.now(timezone.utc).isoformat()}
    try:
        if not pdf_path.exists():
            if os.name == "nt":
                # Use normal OS TLS validation; bundled Python lacks its CA roots.
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "$ErrorActionPreference='Stop'; try { Invoke-WebRequest -UseBasicParsing -Uri '"
                     + url.replace("'", "''") + "' -OutFile '"
                     + str(pdf_path).replace("'", "''")
                     + "' -TimeoutSec 25 } catch { Write-Output $_.Exception.Message; exit 1 }"],
                    capture_output=True, timeout=35,
                )
                if result.returncode:
                    raise RuntimeError(result.stdout.decode("utf-8", errors="replace").strip()[:300])
                body = pdf_path.read_bytes()
                record["retrieval_method"] = "Invoke-WebRequest; normal OS TLS validation"
            else:
                with urlopen(url, timeout=25) as response:
                    body = response.read(20 * 1024 * 1024 + 1)
                    record["final_url"] = response.url
                    record["http_status"] = response.status
                record["retrieval_method"] = "urllib; default TLS validation"
            if len(body) > 20 * 1024 * 1024:
                raise ValueError("Selected source exceeds 20 MiB limit")
            if not body.startswith(b"%PDF"):
                raise ValueError("Selected source did not return a PDF")
            pdf_path.write_bytes(body)
        else:
            record["retrieval_method"] = "cached public PDF previously fetched by Invoke-WebRequest; normal OS TLS validation"
        body = pdf_path.read_bytes()
        record.update(sha256=sha256(body).hexdigest(), bytes=len(body),
                      local_path=str(pdf_path), status="full-text-local")
        reader = PdfReader(pdf_path)
        record["pdf_pages"] = len(reader.pages)
        parts = []
        for i, page in enumerate(reader.pages):
            parts.append(f"\n\n--- PDF page {i+1} ---\n" + (page.extract_text() or ""))
        (CACHE / (source_id + ".txt")).write_text("".join(parts), encoding="utf-8")
        doc = pdfium.PdfDocument(str(pdf_path))
        for i in pages:
            doc[i].render(scale=1.5).to_pil().save(CACHE / f"{source_id}-p{i+1}.png")
        record["rendered_pdf_pages_1based"] = [i+1 for i in pages]
    except Exception as exc:
        record.update(status="fetch-or-inspection-failed", error=type(exc).__name__ + ": " + str(exc))
    return record


if __name__ == "__main__":
    CACHE.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(inspect, SOURCES.items()))
    (ROOT / "public-source-manifest-001.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k not in {"local_path"}}
                      for r in records], ensure_ascii=False, indent=2))
