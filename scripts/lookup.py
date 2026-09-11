#!/usr/bin/env python3
"""Recall-first Metabase docs lookup. Run; do not read this file into context.

Usage:
  python3 lookup.py "each customer should only see their own orders"
  python3 lookup.py --rebuild "embed a chart without login"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
GRAPH = ROOT / "graph"
INDEX_PATH = GRAPH / "index.json"
CONCEPTS_PATH = GRAPH / "concepts.json"

STOP = {
    "a", "an", "the", "to", "of", "in", "on", "for", "and", "or", "with",
    "how", "do", "i", "we", "my", "our", "is", "it", "this", "that", "can",
    "be", "from", "into", "about", "using", "use", "want", "need", "please",
    "metabase", "docs", "documentation", "page", "just", "like", "some",
}

SKIP_BODY_DIRS = ("embedding/sdk/api/snippets", "embedding/eajs/snippets")

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
HEADING = re.compile(r"^#{1,3} (.+)$", re.M)


def load_concepts() -> dict:
    return json.loads(CONCEPTS_PATH.read_text())


def yaml_field(block: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.+)$", block, re.M)
    if not m:
        return ""
    return m.group(1).strip().strip("\"'")


def yaml_list(block: str, key: str) -> list[str]:
    m = re.search(rf"^{key}:\n((?:  - .+\n)+)", block, re.M)
    if not m:
        return []
    return [re.sub(r"^\s*-\s*", "", line).strip() for line in m.group(1).splitlines() if line.strip()]


def should_skip(rel: str, skip_parts: list[str]) -> bool:
    return any(part in rel for part in skip_parts)


def extract_file(path: Path) -> dict | None:
    rel = str(path.relative_to(SOURCE))
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    fm = ""
    body = raw
    m = FRONTMATTER.match(raw)
    if m:
        fm = m.group(1)
        body = raw[m.end() :]
    title = yaml_field(fm, "title") or (HEADING.search(body).group(1) if HEADING.search(body) else path.stem)
    summary = yaml_field(fm, "summary")
    redirects = yaml_list(fm, "redirect_from")
    headings = [h.strip() for h in HEADING.findall(body)][:40]
    topic = rel.split("/")[0]
    text = re.sub(r"\{%.*?%\}", " ", body)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-zA-Z0-9./_-]+", " ", text).lower()
    return {
        "path": rel,
        "title": title,
        "summary": summary,
        "redirects": redirects,
        "headings": headings,
        "topic_dir": topic,
        "stem": path.stem.replace("_", "-"),
        "text": text[:6000],
        "is_hub": path.stem in {"start", "index", "introduction", "overview"},
        "is_snippet": "snippets" in rel,
    }


def build_index(concepts: dict) -> dict:
    skip = concepts.get("skip_path_parts", [])
    files = []
    for path in SOURCE.rglob("*.md"):
        rel = str(path.relative_to(SOURCE))
        if should_skip(rel, skip):
            continue
        rec = extract_file(path)
        if rec:
            files.append(rec)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"files": files}
    INDEX_PATH.write_text(json.dumps(payload))
    return payload


def ensure_source() -> None:
    """Fetch Metabase docs if this install has no source/ snapshot."""
    if SOURCE.exists() and any(SOURCE.rglob("*.md")):
        return
    SOURCE.mkdir(parents=True, exist_ok=True)
    import shutil
    import subprocess
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="metabase-docs-"))
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--filter=blob:none",
                "--sparse",
                "https://github.com/metabase/metabase.git",
                str(tmp),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(tmp), "sparse-checkout", "set", "docs"],
            check=True,
            capture_output=True,
        )
        src = tmp / "docs"
        if not src.exists():
            raise RuntimeError("sparse checkout did not include docs/")
        shutil.copytree(src, SOURCE, dirs_exist_ok=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def load_index(concepts: dict, rebuild: bool) -> dict:
    ensure_source()
    if rebuild or not INDEX_PATH.exists():
        return build_index(concepts)
    return json.loads(INDEX_PATH.read_text())


def norm(q: str) -> str:
    q = q.lower().replace("{{", " mustache ")
    q = re.sub(r"[^a-z0-9.+_-]+", " ", q)
    return re.sub(r"\s+", " ", q).strip()


def tokens(q: str) -> list[str]:
    return [t for t in q.split() if t not in STOP and len(t) > 1]


def expand(query: str, concepts: dict) -> dict:
    q = norm(query)
    focus: set[str] = set()
    broad: set[str] = set()
    related_c: set[str] = set()
    activated_topics: set[str] = set()
    matched_intents: list[str] = []

    for intent in concepts["intents"]:
        if any(p in q for p in intent["phrases"]):
            matched_intents.append(intent["id"])
            broad.update(intent.get("concepts", []))
            related_c.update(intent.get("related_concepts", []))
            activated_topics.update(intent.get("topics", []))

    aliases = concepts["aliases"]
    for phrase in sorted(aliases, key=len, reverse=True):
        if phrase == "dropdown" and "sql" not in q and "native" not in q:
            continue
        if phrase == "react" and "react" not in q:
            continue
        if phrase in q or phrase.replace(" ", "-") in q:
            for c in aliases[phrase]:
                focus.add(c)

    # Alias hits are the user's actual wording — keep them out of the broad dump
    broad -= focus
    related_c -= focus
    related_c -= broad

    related_topics: set[str] = set()
    for topic in activated_topics:
        related_topics.update(concepts["topics"].get(topic, {}).get("related", []))
    related_topics -= activated_topics

    return {
        "query": q,
        "terms": tokens(q),
        "focus": sorted(focus),
        "broad": sorted(broad),
        "related_concepts": sorted(related_c),
        "concepts": sorted(focus | broad),
        "topics": sorted(activated_topics),
        "related_topics": sorted(related_topics),
        "intents": matched_intents,
    }


def dir_to_topic(topic_dir: str, concepts: dict) -> str | None:
    for tid, cfg in concepts["topics"].items():
        if topic_dir in cfg["dirs"]:
            return tid
    return None


def concept_hit(rec: dict, concept: str) -> str | None:
    """Return match strength: stem, title, redirect, path, or None."""
    cspace = concept.replace("-", " ")
    stem = rec["stem"]
    title = rec["title"].lower()
    path = rec["path"].lower()
    summary = rec["summary"].lower()
    red = " ".join(rec["redirects"]).lower()
    if concept == stem or title == cspace:
        return "stem"
    compact_red = red.replace("-", "/").replace("_", "")
    if concept.replace("-", "") in compact_red.replace("/", "").replace("-", ""):
        return "redirect"
    if concept in path:
        return "path"
    if cspace in summary:
        return "summary"
    return None


def score_file(rec: dict, exp: dict, concepts: dict) -> tuple[float, list[str]]:
    if rec["is_snippet"]:
        return 0.0, []
    reasons = []
    score = 0.0
    blob_title = rec["title"].lower()
    blob_sum = rec["summary"].lower()
    blob_path = rec["path"].lower()
    blob_head = " ".join(rec["headings"]).lower()
    focus = set(exp.get("focus") or [])
    broad = set(exp.get("broad") or [])
    related_c = set(exp.get("related_concepts") or [])

    def apply_concepts(group: set[str], weights: dict[str, float], label: str) -> None:
        nonlocal score
        for c in group:
            kind = concept_hit(rec, c)
            if not kind:
                continue
            # Directory-wide tokens (sdk) match every file in that folder — keep only hubs
            if kind == "path" and c in {"sdk", "modular-embedding"} and not rec["is_hub"]:
                if rec["stem"] not in {"introduction", "quickstart", "chart", "dashboard", "guest-embedding"}:
                    score += 4
                    reasons.append(f"{label}-weak:{c}")
                    continue
            score += weights[kind]
            reasons.append(f"{label}:{kind}:{c}")

    apply_concepts(focus, {"stem": 55, "redirect": 48, "title": 55, "path": 16, "summary": 22}, "focus")
    apply_concepts(broad, {"stem": 36, "redirect": 32, "title": 36, "path": 8, "summary": 14}, "broad")
    apply_concepts(related_c, {"stem": 18, "redirect": 16, "title": 18, "path": 4, "summary": 8}, "rel")

    # Query terms: title/summary only (body matches cause false positives)
    for term in exp["terms"]:
        if term in blob_title:
            score += 8
        elif term in blob_sum:
            score += 4
        elif term in blob_path.split("/")[-1]:
            score += 3

    tid = dir_to_topic(rec["topic_dir"], concepts)
    if tid and tid in exp["topics"] and rec["is_hub"]:
        score += 4
        reasons.append(f"hub:{tid}")

    if rec["stem"] == "data-isolation-methods" and "isolate-tenant-data" in exp["intents"]:
        score += 25
        reasons.append("isolation-chooser")

    q = exp.get("query", "")
    if rec["stem"] in {"guest-embedding", "public-links"} and any(
        p in q for p in ("without", "no login", "no account", "guest", "not log")
    ):
        score += 40
        reasons.append("no-login-bias")

    return score, reasons[:8]


def folder_bucket(path: str) -> str:
    parts = path.split("/")
    return "/".join(parts[:2]) if len(parts) > 1 else parts[0]


def lookup(query: str, concepts: dict, index: dict) -> dict:
    exp = expand(query, concepts)
    scored = []
    for rec in index["files"]:
        s, reasons = score_file(rec, exp, concepts)
        if s > 0:
            scored.append((s, rec, reasons))
    scored.sort(key=lambda x: (-x[0], x[1]["path"]))

    primary, related, seen = [], [], set()
    buckets: dict[str, int] = {}

    def pack(item) -> dict:
        s, rec, reasons = item
        return {
            "score": round(s, 1),
            "path": rec["path"],
            "read_path": str(SOURCE / rec["path"]),
            "title": rec["title"],
            "summary": rec["summary"][:220],
            "why": reasons or ["text-match"],
            "url": "https://www.metabase.com/docs/latest/" + rec["path"][:-3],
        }

    top = scored[0][0] if scored else 0
    primary_floor = max(28.0, 0.50 * top) if top else 28.0
    related_floor = max(18.0, 0.32 * top) if top else 18.0
    focus = set(exp.get("focus") or [])

    for s, rec, reasons in scored:
        if rec["path"] in seen:
            continue
        is_focus_stem = rec["stem"] in focus or any(
            r.startswith("focus:stem:") or r.startswith("broad:stem:") or r == "isolation-chooser"
            for r in reasons
        )
        if s < primary_floor and not is_focus_stem:
            continue
        bucket = folder_bucket(rec["path"])
        if buckets.get(bucket, 0) >= 2:
            continue
        seen.add(rec["path"])
        buckets[bucket] = buckets.get(bucket, 0) + 1
        primary.append(pack((s, rec, reasons)))
        if len(primary) >= 5:
            break

    for s, rec, reasons in scored:
        if rec["path"] in seen:
            continue
        if s < related_floor:
            continue
        if rec["is_hub"] and s < 0.45 * top:
            continue
        seen.add(rec["path"])
        related.append(pack((s, rec, reasons)))
        if len(related) >= 4:
            break

    abstract = not exp["intents"] and len(exp.get("focus") or []) < 1
    miss_risk = abstract or (not primary)

    return {
        "query": query,
        "interpreted_as": {
            "intents": exp["intents"],
            "focus": exp.get("focus") or [],
            "broad": exp.get("broad") or [],
            "related_concepts": exp.get("related_concepts") or [],
            "topics": exp["topics"],
        },
        "miss_risk": miss_risk,
        "protocol": (
            "LOW CONFIDENCE: read PRIMARY, then grep source/ for remaining nouns."
            if miss_risk
            else "Read PRIMARY only. ALSO CHECK is optional — do not treat those as required."
        ),
        "skill_root": str(ROOT),
        "primary": primary,
        "related_might_also_apply": related,
        "official_url_pattern": "https://www.metabase.com/docs/latest/<path-without-md>",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Recall-first Metabase docs lookup")
    p.add_argument("query", nargs="+", help="User question, even if abstract")
    p.add_argument("--rebuild", action="store_true")
    p.add_argument("--json", action="store_true", help="JSON only")
    args = p.parse_args()
    query = " ".join(args.query)
    concepts = load_concepts()
    index = load_index(concepts, args.rebuild)
    result = lookup(query, concepts, index)
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"SKILL_ROOT: {result['skill_root']}")
    print(f"QUERY: {result['query']}")
    interp = result["interpreted_as"]
    print(f"INTENTS: {', '.join(interp['intents']) or '(none — treating as abstract)'}")
    print(f"FOCUS: {', '.join(interp.get('focus') or []) or '(none)'}")
    print(f"BROAD: {', '.join(interp.get('broad') or []) or '(none)'}")
    print(f"TOPICS: {', '.join(interp['topics']) or '(none)'}")
    print(f"MISS_RISK: {result['miss_risk']}")
    print(f"DO: {result['protocol']}")
    print("\nPRIMARY (Read these absolute paths):")
    if not result["primary"]:
        print("  (no ranked hits — grep source/ and fetch live docs)")
    for i, hit in enumerate(result["primary"], 1):
        print(f"  {i}. {hit['read_path']}")
        print(f"     {hit['title']}  [{hit['score']}] {', '.join(hit['why'])}")
        print(f"     {hit['url']}")
        if hit["summary"]:
            print(f"     {hit['summary']}")
    if result["related_might_also_apply"]:
        print("\nALSO CHECK (optional, may be weaker matches):")
        for hit in result["related_might_also_apply"]:
            print(f"  - {hit['read_path']}  ({hit['title']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
