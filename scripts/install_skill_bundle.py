import json
from pathlib import Path
import httpx
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MANIFEST = Path(__file__).resolve().parent / "skill_bundle_sources.json"


def safe_name_from_url(url: str) -> str:
    name = url.rstrip("/").split("/")[-1].replace(".py", "")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name.strip("_").lower()


def install():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    urls = data.get("sources", [])
    ok = 0
    failed = 0

    for url in urls:
        try:
            r = httpx.get(url, timeout=30)
            r.raise_for_status()
            code = r.text
            if "def run(" not in code:
                raise ValueError("run() not found")
            skill_name = safe_name_from_url(url)
            target = SKILLS_DIR / f"{skill_name}.py"
            target.write_text(code, encoding="utf-8")
            ok += 1
            print(f"✅ installed {skill_name}")
        except Exception as e:
            failed += 1
            print(f"❌ failed {url}: {e}")

    print(f"\nBundle install done: ok={ok}, failed={failed}, total={len(urls)}")


if __name__ == "__main__":
    install()
