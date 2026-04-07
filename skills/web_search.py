import httpx

DDG_API = "https://api.duckduckgo.com/"


def run(query: str = "", max_results: int = 5):
    query = (query or "").strip()
    if not query:
        return "❌ Nedostaje parametar query."

    resp = httpx.get(DDG_API, params={
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    out = [f"🔎 Rezultati za: {query}"]
    if data.get("AbstractText"):
        out.append(f"- {data.get('Heading') or 'Odgovor'}: {data['AbstractText']}")
        if data.get("AbstractURL"):
            out.append(f"  {data['AbstractURL']}")

    related = data.get("RelatedTopics") or []
    count = 0
    for item in related:
        if isinstance(item, dict) and item.get("Text") and item.get("FirstURL"):
            out.append(f"- {item['Text']}\n  {item['FirstURL']}")
            count += 1
            if count >= max(1, int(max_results)):
                break

    if count == 0 and not data.get("AbstractText"):
        # Fallback: Wikipedia open search
        wiki = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": query, "limit": max(1, int(max_results)), "namespace": 0, "format": "json"},
            timeout=20
        )
        wiki.raise_for_status()
        w = wiki.json()
        titles = w[1] if len(w) > 1 else []
        descs = w[2] if len(w) > 2 else []
        links = w[3] if len(w) > 3 else []
        if titles:
            out = [f"🔎 Wikipedia fallback za: {query}"]
            for i, t in enumerate(titles[:max(1, int(max_results))]):
                d = descs[i] if i < len(descs) else ""
                l = links[i] if i < len(links) else ""
                out.append(f"- {t}: {d}\n  {l}".strip())
            return "\n".join(out)
        return f"Nisam našao rezultate za: {query}"

    return "\n".join(out)
