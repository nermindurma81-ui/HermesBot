def run(text: str = "", max_sentences: int = 3):
    text = (text or "").strip()
    if not text:
        return "❌ Nedostaje text."
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        return "❌ Ne mogu izdvojiti rečenice."
    return "📝 Sažetak:\n" + ". ".join(sentences[:max(1, int(max_sentences))]) + "."
