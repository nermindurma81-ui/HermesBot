import ast
import inspect
import json
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]


def parse_all_python_files():
    py_files = [p for p in ROOT.rglob("*.py") if ".venv" not in p.parts]
    errors = []
    for p in py_files:
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except Exception as e:
            errors.append((str(p), str(e)))
    return py_files, errors


def validate_skill_modules():
    skills_dir = ROOT / "skills"
    errors = []
    checked = 0
    for p in sorted(skills_dir.glob("*.py")):
        checked += 1
        try:
            spec = importlib.util.spec_from_file_location(p.stem, p)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if not hasattr(mod, "run") or not callable(mod.run):
                errors.append((p.name, "missing callable run()"))
                continue
            inspect.signature(mod.run)
        except Exception as e:
            errors.append((p.name, str(e)))
    return checked, errors


def validate_manifests():
    manifest = ROOT / "scripts" / "skill_bundle_sources.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    unique = len(set(sources))
    return {
        "total": len(sources),
        "unique": unique,
        "all_https_py": all(s.startswith("https://") and s.endswith(".py") for s in sources),
    }


def main():
    py_files, py_errors = parse_all_python_files()
    checked_skills, skill_errors = validate_skill_modules()
    manifest = validate_manifests()

    print(f"python_files={len(py_files)}")
    print(f"skill_modules={checked_skills}")
    print(f"manifest_total={manifest['total']}, manifest_unique={manifest['unique']}, https_py={manifest['all_https_py']}")

    if py_errors:
        print("PY_ERRORS:")
        for f, e in py_errors:
            print(f" - {f}: {e}")
    if skill_errors:
        print("SKILL_ERRORS:")
        for f, e in skill_errors:
            print(f" - {f}: {e}")

    if py_errors or skill_errors or not manifest["all_https_py"] or manifest["total"] != manifest["unique"]:
        raise SystemExit(1)

    print("DEEP_SANITY_OK")


if __name__ == "__main__":
    main()
