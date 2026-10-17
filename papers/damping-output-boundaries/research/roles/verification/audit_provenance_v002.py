"""Reconstruct initial source bytes from the single pre-freeze timestamp edit."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent/"ideation/round-001.md"


def main():
    current = SOURCE.read_bytes()
    needle = "记录冻结2026-10-17 08:59 +08:00".encode("utf-8")
    prior = "记录冻结2026-10-17 09:00 +08:00".encode("utf-8")
    assert current.count(needle) == 1
    reconstructed = current.replace(needle,prior,1)
    oldhash = hashlib.sha256(reconstructed).hexdigest()
    newhash = hashlib.sha256(current).hexdigest()
    assert oldhash == "affe7a13dbfa0465af8239de0af0c770b15e3bdf1c7e6b322d758c1f1c8671c7"
    assert newhash == "c27ba79e4330f4a717c434188222a5f0ea7d0187cc374f5fa9e7dc5025f52671"
    payload = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "source_path_relative":"../ideation/round-001.md",
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "current_source_sha256":newhash,
        "reconstructed_initial_source_sha256":oldhash,
        "single_replacement_current_to_initial":{"from":needle.decode(),"to":prior.decode(),"occurrences":1},
        "current_bytes":len(current),"initial_bytes":len(reconstructed),
        "CRLF_count_current":current.count(b"\r\n"),
        "LF_count_current":current.count(b"\n"),
        "changed_byte_offsets":[j for j,(x,y) in enumerate(zip(current,reconstructed)) if x!=y],
        "scope":"No frozen source/report/results modified. Only the timestamp differs; initial byte string independently reconstructs the originally observed SHA256. No mathematical experiment rerun."
    }
    (HERE/"provenance-V002.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
