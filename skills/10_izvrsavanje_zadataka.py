from pathlib import Path


def run(section: str = ""):
    md_path = Path(__file__).with_suffix('.md')
    if not md_path.exists():
        return f"❌ Nedostaje markdown fajl: {md_path.name}"

    content = md_path.read_text(encoding='utf-8')
    if not section.strip():
        return content

    key = section.strip().lower()
    lines = content.splitlines()
    out = []
    capture = False
    current_level = None

    for line in lines:
        l = line.strip()
        if l.startswith('#'):
            level = len(l) - len(l.lstrip('#'))
            title = l[level:].strip().lower()
            if key in title:
                capture = True
                current_level = level
                out.append(line)
                continue
            if capture and level <= current_level:
                break

        if capture:
            out.append(line)

    if out:
        return '\n'.join(out).strip()

    return f"ℹ️ Sekcija '{section}' nije pronađena u {md_path.name}."
