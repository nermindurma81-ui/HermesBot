#!/usr/bin/env python3
"""Select active skills to inject into Hermes system prompt context."""

from __future__ import annotations

import argparse
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "memory" / "ACTIVE_SKILLS.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*", help="Skill names to activate")
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"skills": args.skills}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Active skills saved to {OUT}")


if __name__ == "__main__":
    main()
