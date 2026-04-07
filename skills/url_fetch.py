import httpx


def run(url: str = ""):
    url = (url or "").strip()
    if not url:
        return "❌ Nedostaje url."
    if not url.startswith(("http://", "https://")):
        return "❌ URL mora početi sa http:// ili https://"
    try:
        r = httpx.get(url, timeout=20, follow_redirects=True)
        text = r.text[:3000]
        return f"🌐 {url}\nstatus={r.status_code}\n\n{text}"
    except Exception as e:
        return f"❌ Fetch error: {e}"
