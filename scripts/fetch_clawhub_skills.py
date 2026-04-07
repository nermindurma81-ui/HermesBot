#!/usr/bin/env python3
"""Fetch Python skills from ClawHub/raw URLs and save into local skills/ directory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG = ROOT / "scripts" / "skill_bundle_sources.json"


def safe_name(raw: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]", "_", raw or "").strip("_").lower()
    return re.sub(r"_+", "_", name)


def fetch_and_save(url: str) -> tuple[bool, str]:
    parsed_name = safe_name(Path(url).name.replace(".py", ""))
    if not parsed_name:
        return False, f"Invalid name from URL: {url}"

    try:
        resp = httpx.get(url, timeout=25)
        resp.raise_for_status()
        code = resp.text
    except Exception as e:
        return False, f"Download failed ({url}): {e}"

    if "def run(" not in code:
        return False, f"Skipped {url}: no def run(...) found"

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    out = SKILLS_DIR / f"{parsed_name}.py"
    out.write_text(code, encoding="utf-8")
    return True, f"Installed {parsed_name} from {url}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", default=[], help="Raw .py URL (can be passed multiple times)")
    ap.add_argument("--from-catalog", action="store_true", help="Install URLs from scripts/skill_bundle_sources.json")
    args = ap.parse_args()

    urls = list(args.url)
    if args.from_catalog and CATALOG.exists():
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        urls.extend(data.get("urls", []))

    urls = [u.strip() for u in urls if u.strip()]
    if not urls:
        print("No URLs provided. Use --url <raw_py_url> or --from-catalog")
        return

    ok = 0
    fail = 0
    for u in urls:
        success, msg = fetch_and_save(u)
        print(("✅ " if success else "❌ ") + msg)
        ok += int(success)
        fail += int(not success)

    print(f"Done. installed={ok} failed={fail}")


if __name__ == "__main__":
    main()
