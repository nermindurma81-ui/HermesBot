"""Skill loader for SKILL.md-based dynamic context injection."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

SKILLS_DIR = Path(os.getenv("SKILLS_DIR", "skills"))


def list_available_skills() -> list[dict]:
    skills: list[dict] = []
    if not SKILLS_DIR.exists():
        return skills

    for skill_file in SKILLS_DIR.rglob("SKILL.md"):
        skill_name = skill_file.parent.name
        skills.append(
            {
                "name": skill_name,
                "path": str(skill_file),
                "description": _extract_description(skill_file),
            }
        )
    return skills


def load_skill(skill_name: str) -> Optional[str]:
    direct = SKILLS_DIR / skill_name / "SKILL.md"
    if direct.exists():
        return direct.read_text(encoding="utf-8")

    for skill_file in SKILLS_DIR.rglob("SKILL.md"):
        if skill_file.parent.name.lower() == skill_name.lower():
            return skill_file.read_text(encoding="utf-8")
    return None


def save_skill(skill_name: str, content: str) -> bool:
    try:
        target_dir = SKILLS_DIR / skill_name
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False


def detect_relevant_skills(user_message: str) -> list[str]:
    text = (user_message or "").lower()
    if not text:
        return []

    triggered: list[str] = []
    for skill in list_available_skills():
        name = (skill.get("name") or "").strip()
        if not name:
            continue

        desc = (skill.get("description") or "").lower()
        if name.lower() in text:
            triggered.append(name)
            continue

        keywords = _extract_trigger_keywords(desc)
        if any(kw in text for kw in keywords):
            triggered.append(name)

    return triggered


def build_skill_context(skill_names: list[str]) -> str:
    if not skill_names:
        return ""

    parts = ["=== ACTIVE SKILLS ==="]
    for name in skill_names:
        content = load_skill(name)
        if content:
            parts.append(f"--- SKILL: {name} ---\n{content}")
    return "\n\n".join(parts)


def inject_skills_into_system_prompt(base_prompt: str, skill_context: str) -> str:
    if not skill_context:
        return base_prompt
    return f"{base_prompt}\n\n{skill_context}"


def _extract_description(skill_file: Path) -> str:
    try:
        content = skill_file.read_text(encoding="utf-8")
        fm_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', content)
        if fm_match:
            return fm_match.group(1).strip()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith(("---", "#")):
                return line[:200]
    except Exception:
        pass
    return ""


def _extract_trigger_keywords(description: str) -> list[str]:
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "use",
        "when",
        "this",
        "that",
        "with",
        "for",
        "and",
        "or",
        "to",
        "in",
        "on",
        "at",
        "of",
    }
    words = re.findall(r"\b[a-z]{3,}\b", description)
    return [w for w in words if w not in stop_words]
