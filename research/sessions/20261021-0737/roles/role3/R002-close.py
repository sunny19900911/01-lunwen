"""Close the R002 reused-source evidence package without altering old evidence."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROLE = Path(__file__).resolve().parent
REPO = ROLE.parents[4]
WORKSPACE = REPO.parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat()

def fingerprint(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}

def write_new(name, value):
    with (ROLE / name).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

def main():
    outputs = ["R002-manifest.json", "R002-validation.json", "R002-freeze.json"]
    if any((ROLE / name).exists() for name in outputs):
        raise SystemExit("Refusing to overwrite an R002 closure output")
    source_specs = [
        (REPO / "papers/damping-output-boundaries/research/roles/novelty/engineering-session006/R001/local-cache/DeDomenico-Hajirasouliha2021.pdf",
         "aee1baa65e6d3ed8ab2bae3a19e48ceef371101229cd36ae3802b342152ec0fd"),
        (WORKSPACE / "W6-重燃强连接双塔/01-文献/参考文献-Liu2004-性能目标与模态阻尼配置.pdf",
         "9e8a3b997f91d57a0f816b0e9f859cc8f00d1d7510aa2b7eb1e1eb15b14a1d17"),
    ]
    sources = []
    for path, expected in source_specs:
        item = fingerprint(path)
        item.update(expected_sha256=expected,
                    matches_prior_fingerprint=(item["sha256"] == expected),
                    original_page_images_reopened_this_round=False,
                    body_reextracted_this_round=False,
                    repository_fulltext_remains_local=True)
        sources.append(item)
    input_names = [
        "AGENTS.md", ".agents/skills/research-paper-lab/SKILL.md",
        ".agents/skills/research-paper-lab/references/literature-review.md",
        "docs/多角色论文研究框架.md", "research/sessions/20261021-0737/plan.md",
        "papers/damping-output-boundaries/literature/index.md",
        "papers/damping-output-boundaries/research/roles/literature/liu2004-followup.md",
        "papers/damping-output-boundaries/research/roles/novelty/engineering-session006/R001/local-cache/DeDomenico-Hajirasouliha2021.pdf.fetch.json",
    ]
    manifest = {"task": "role3 R002", "created_at": NOW,
                "mode": "reuse previously verified original-source evidence",
                "sources": sources,
                "records_read_this_round": [fingerprint(REPO / name) for name in input_names],
                "new_web_queries": 0, "new_downloads": 0,
                "adopted_primary_sources": 2,
                "excluded_repeat_sources": ["柳博哲/汪梦甫2024", "Song/Maxwell基础"],
                "evidence_table": fingerprint(ROLE / "R002-evidence-short-table.md")}
    write_new("R002-manifest.json", manifest)
    validation = {"task": "role3 R002", "closed_at": NOW,
                  "first_observed_clock": "2026-10-21T07:57:50+08:00",
                  "later_observed_clock": "2026-10-21T20:17:28+08:00",
                  "system_clock_confirmed": "2026-10-21T20:17:52+08:00",
                  "requested_delivery_boundary": "2026-10-21T08:10:00+08:00",
                  "within_original_delivery_boundary": False,
                  "time_gap_cause": "unknown; no claim of continuous execution",
                  "new_user_request": "你再继续写90分钟把。",
                  "first_clock_after_new_request": "2026-10-21T20:20:14+08:00",
                  "new_request_forwarded_to_existing_main": True,
                  "old_session_deadline_extended_in_place": False,
                  "original_page_rereview_this_round": False,
                  "two_source_fingerprints_match": all(s["matches_prior_fingerprint"] for s in sources),
                  "source_specific_writable_sentences": True,
                  "exact_page_equation_figure_locations_from_prior_verified_records": True,
                  "short_table_sent_before_manifest": True,
                  "references_added_for_count_only": False,
                  "same_conditions_priority_or_acceptance_claim": False,
                  "manuscript_shared_ledger_git_etabs_mutations": False,
                  "new_chats_or_agents": False}
    write_new("R002-validation.json", validation)
    freeze = {"task": "role3 R002", "frozen_at": NOW, "immutable": True,
              "files": [fingerprint(ROLE / name) for name in
                        ["R002-evidence-short-table.md", "R002-manifest.json",
                         "R002-validation.json", "R002-close.py"]]}
    write_new("R002-freeze.json", freeze)
    print(json.dumps({"validation": validation,
                      "report": fingerprint(ROLE / "R002-evidence-short-table.md"),
                      "freeze": fingerprint(ROLE / "R002-freeze.json")},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
