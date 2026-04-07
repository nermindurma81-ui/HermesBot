import httpx


def run(base: str = "EUR", target: str = "USD"):
    base = (base or "EUR").upper().strip()
    target = (target or "USD").upper().strip()
    try:
        r = httpx.get(
            "https://api.exchangerate.host/convert",
            params={"from": base, "to": target, "amount": 1},
            timeout=20,
        )
        r.raise_for_status()
        d = r.json()
        if not d.get("result"):
            return f"❌ Kurs nije dostupan za {base}->{target}"
        return f"💱 1 {base} = {d['result']:.6f} {target}"
    except Exception as e:
        return f"❌ Rate error: {e}"
