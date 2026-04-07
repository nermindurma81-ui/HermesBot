def run(expression: str = ""):
    expression = (expression or "").strip()
    if not expression:
        return "❌ Nedostaje expression."
    allowed = set("0123456789+-*/(). %")
    if any(ch not in allowed for ch in expression):
        return "❌ Nedozvoljeni znakovi u izrazu."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"🧮 {expression} = {result}"
    except Exception as e:
        return f"❌ Greška u računu: {e}"
