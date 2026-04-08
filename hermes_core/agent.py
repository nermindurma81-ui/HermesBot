# hermes_core/agent.py
# HermesBot — Kompletan AI Agent Engine
# Ollama (primary) + HuggingFace Inference API (fallback)

import os
import json
import datetime
import requests
from pathlib import Path
from typing import Generator, Optional

# ─── Konfiguracija ────────────────────────────────────────────────────────────

OLLAMA_HOST   = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL  = os.environ.get("OLLAMA_MODEL", "llama3.2")
HF_TOKEN      = os.environ.get("HF_TOKEN", "")
HF_MODEL      = os.environ.get("HF_MODEL", "google/gemma-3-4b-it")
BOT_NAME      = os.environ.get("BOT_NAME", "HermesBot")
MEMORY_ENABLED = os.environ.get("MEMORY_ENABLED", "true").lower() == "true"
MAX_CONTEXT   = int(os.environ.get("MAX_CONTEXT_MESSAGES", "20"))

MEMORY_FILE   = Path("memory/MEMORY.md")
SKILLS_DIR    = Path("skills")

DEFAULT_SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    f"You are {BOT_NAME}, a helpful AI assistant. Be concise, accurate and friendly."
)

# ─── Memorija ─────────────────────────────────────────────────────────────────

def load_memory() -> str:
    if not MEMORY_ENABLED:
        return ""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MEMORY_FILE.exists():
        return MEMORY_FILE.read_text(encoding="utf-8")
    return ""


def save_memory(content: str) -> None:
    if not MEMORY_ENABLED:
        return
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(content, encoding="utf-8")


def remember(key: str, value: str) -> str:
    memory = load_memory()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] **{key}**: {value}"
    if key in memory:
        # Ažuriraj postojeći
        lines = memory.splitlines()
        new_lines = []
        for line in lines:
            if f"**{key}**" in line:
                new_lines.append(entry.strip())
            else:
                new_lines.append(line)
        save_memory("\n".join(new_lines))
    else:
        save_memory(memory + entry)
    return f"✅ Zapamtio sam: **{key}** = {value}"


def recall_memory(query: str = "") -> str:
    memory = load_memory()
    if not memory:
        return "Memorija je prazna."
    if query:
        lines = [l for l in memory.splitlines() if query.lower() in l.lower()]
        return "\n".join(lines) if lines else f"Ništa pronađeno za '{query}'."
    return memory

# ─── Skillovi ─────────────────────────────────────────────────────────────────

def list_skills() -> list[dict]:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for skill_file in SKILLS_DIR.rglob("SKILL.md"):
        name = skill_file.parent.name
        description = _extract_skill_description(skill_file)
        skills.append({"name": name, "path": str(skill_file), "description": description})
    return skills


def load_skill(name: str) -> Optional[str]:
    direct = SKILLS_DIR / name / "SKILL.md"
    if direct.exists():
        return direct.read_text(encoding="utf-8")
    for f in SKILLS_DIR.rglob("SKILL.md"):
        if f.parent.name.lower() == name.lower():
            return f.read_text(encoding="utf-8")
    return None


def save_skill_file(name: str, content: str) -> bool:
    try:
        skill_dir = SKILLS_DIR / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"[agent] Greška pri čuvanju skilla: {e}")
        return False


def detect_relevant_skills(message: str) -> list[str]:
    import re
    triggered = []
    msg_lower = message.lower()
    stop = {"the","a","an","is","are","use","when","this","that","with","for","and","or","to","in","on","at","of"}
    for skill in list_skills():
        name = skill["name"].lower()
        desc = skill["description"].lower()
        if name in msg_lower:
            triggered.append(skill["name"])
            continue
        keywords = [w for w in re.findall(r'\b[a-z]{3,}\b', desc) if w not in stop]
        if any(kw in msg_lower for kw in keywords):
            triggered.append(skill["name"])
    return triggered


def build_skill_context(skill_names: list[str]) -> str:
    if not skill_names:
        return ""
    parts = ["=== ACTIVE SKILLS ===\n"]
    for name in skill_names:
        content = load_skill(name)
        if content:
            parts.append(f"--- SKILL: {name} ---\n{content}\n")
    return "\n".join(parts)


def _extract_skill_description(skill_file: Path) -> str:
    import re
    try:
        content = skill_file.read_text(encoding="utf-8")
        m = re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', content)
        if m:
            return m.group(1).strip()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith(("---", "#")):
                return line[:200]
    except Exception:
        pass
    return ""

# ─── Toolovi ──────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "remember",
        "description": "Pamti informaciju u dugoročnu memoriju",
        "args": {"key": "string", "value": "string"}
    },
    {
        "name": "recall_memory",
        "description": "Pretraži dugoročnu memoriju",
        "args": {"query": "string (opciono)"}
    },
    {
        "name": "list_skills",
        "description": "Listaj dostupne skillove",
        "args": {}
    },
    {
        "name": "read_skill",
        "description": "Pročitaj sadržaj skilla",
        "args": {"name": "string"}
    },
    {
        "name": "save_skill",
        "description": "Sačuvaj novi skill",
        "args": {"name": "string", "content": "string"}
    },
    {
        "name": "ollama_status",
        "description": "Provjeri status Ollama servisa i dostupnih modela",
        "args": {}
    },
    {
        "name": "pull_model",
        "description": "Preuzmi Ollama model",
        "args": {"model": "string"}
    },
]


def execute_tool(tool_name: str, args: dict) -> str:
    """Izvrši tool i vrati rezultat kao string."""
    
    if tool_name == "remember":
        return remember(args.get("key", "info"), args.get("value", ""))

    elif tool_name == "recall_memory":
        return recall_memory(args.get("query", ""))

    elif tool_name == "list_skills":
        skills = list_skills()
        if not skills:
            return "Nema dostupnih skillova. Dodaj .md fajlove u skills/ folder."
        lines = ["**Dostupni skillovi:**\n"]
        for s in skills:
            lines.append(f"• **{s['name']}**: {s['description']}")
        return "\n".join(lines)

    elif tool_name == "read_skill":
        name = args.get("name", "")
        content = load_skill(name)
        return content if content else f"Skill '{name}' nije pronađen."

    elif tool_name == "save_skill":
        name = args.get("name", "")
        content = args.get("content", "")
        if save_skill_file(name, content):
            return f"✅ Skill '{name}' sačuvan u skills/{name}/SKILL.md"
        return f"❌ Greška pri čuvanju skilla '{name}'."

    elif tool_name == "ollama_status":
        try:
            resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                return f"✅ Ollama aktivan.\nModeli: {', '.join(models) if models else 'nema'}"
            return f"⚠️ Ollama odgovorio sa statusom {resp.status_code}"
        except Exception as e:
            return f"❌ Ollama nije dostupan: {e}"

    elif tool_name == "pull_model":
        model = args.get("model", "")
        try:
            resp = requests.post(
                f"{OLLAMA_HOST}/api/pull",
                json={"name": model},
                timeout=300,
                stream=True
            )
            lines = []
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        lines.append(data["status"])
            return "\n".join(lines[-5:]) if lines else "Model pull završen."
        except Exception as e:
            return f"❌ Greška: {e}"

    return f"❌ Nepoznati tool: '{tool_name}'"


def parse_tool_call(text: str) -> Optional[tuple[str, dict]]:
    """
    Parsira tool poziv iz LLM odgovora.
    Podržava formate:
      <tool>remember</tool><args>{"key":"x","value":"y"}</args>
      [TOOL: remember] {"key":"x","value":"y"}
    """
    import re

    # Format 1: XML-like
    m = re.search(r'<tool>(.*?)</tool>\s*<args>(.*?)</args>', text, re.DOTALL)
    if m:
        tool_name = m.group(1).strip()
        try:
            args = json.loads(m.group(2).strip())
        except Exception:
            args = {}
        return tool_name, args

    # Format 2: [TOOL: name] {...}
    m = re.search(r'\[TOOL:\s*(\w+)\]\s*(\{.*?\})?', text, re.DOTALL)
    if m:
        tool_name = m.group(1).strip()
        try:
            args = json.loads(m.group(2) or "{}")
        except Exception:
            args = {}
        return tool_name, args

    return None

# ─── Backend: Ollama ──────────────────────────────────────────────────────────

def _ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _call_ollama_stream(messages: list, model: str) -> Generator[str, None, None]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }
    with requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        stream=True,
        timeout=120
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data:
                    chunk = data["message"].get("content", "")
                    if chunk:
                        yield chunk
                if data.get("done"):
                    break


def _call_ollama_sync(messages: list, model: str) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

# ─── Backend: HuggingFace Inference API ───────────────────────────────────────

def _format_gemma_prompt(messages: list) -> str:
    """Formatira messages u Gemma chat format."""
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            prompt += f"<start_of_turn>system\n{content}<end_of_turn>\n"
        elif role == "user":
            prompt += f"<start_of_turn>user\n{content}<end_of_turn>\n"
        elif role == "assistant":
            prompt += f"<start_of_turn>model\n{content}<end_of_turn>\n"
    prompt += "<start_of_turn>model\n"
    return prompt


def _call_hf_api(messages: list) -> str:
    if not HF_TOKEN:
        raise Exception("HF_TOKEN nije postavljen.")
    
    hf_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    prompt = _format_gemma_prompt(messages)
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True,
            "return_full_text": False
        }
    }
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(hf_url, headers=headers, json=payload, timeout=60)
    
    if resp.status_code == 503:
        # Model se učitava
        raise Exception("Model se učitava na HF serveru, pokušaj za 20-30 sekundi.")
    
    resp.raise_for_status()
    result = resp.json()
    
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "")
    return str(result)

# ─── Glavni Chat Engine ───────────────────────────────────────────────────────

def build_system_prompt(user_message: str) -> str:
    """Gradi system prompt sa skill kontekstom i memorijom."""
    base = DEFAULT_SYSTEM_PROMPT
    
    # Dodaj memoriju
    memory = load_memory()
    if memory:
        base += f"\n\n=== MEMORIJA ===\n{memory}"
    
    # Dodaj tool instrukcije
    tool_list = "\n".join([
        f"- {t['name']}({', '.join(f'{k}: {v}' for k,v in t['args'].items())}): {t['description']}"
        for t in TOOLS
    ])
    base += f"""

=== DOSTUPNI TOOLOVI ===
Kada trebaš koristiti tool, odgovori u formatu:
<tool>naziv_toola</tool><args>{{"key": "value"}}</args>

{tool_list}

Nakon tool poziva, sačekaj rezultat i nastavi odgovor.
"""
    
    # Dodaj skill kontekst
    relevant = detect_relevant_skills(user_message)
    if relevant:
        skill_ctx = build_skill_context(relevant)
        base += f"\n\n{skill_ctx}"
    
    return base


def chat_stream(
    user_message: str,
    history: list[dict],
    model: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Glavna chat funkcija — vraća generator chunkova teksta.
    
    Args:
        user_message: Poruka korisnika
        history: Lista prethodnih poruka [{"role": "user/assistant", "content": "..."}]
        model: Ollama model (opciono, koristi OLLAMA_MODEL ako nije specificirano)
    
    Yields:
        str: Chunk odgovora
    """
    active_model = model or OLLAMA_MODEL
    system_prompt = build_system_prompt(user_message)
    
    # Gradi messages listu
    messages = [{"role": "system", "content": system_prompt}]
    messages += history[-MAX_CONTEXT:]
    messages.append({"role": "user", "content": user_message})
    
    full_response = ""
    
    try:
        if _ollama_available():
            print(f"[HermesBot] Koristim Ollama ({active_model})")
            for chunk in _call_ollama_stream(messages, active_model):
                full_response += chunk
                yield chunk
        else:
            print("[HermesBot] Ollama nedostupan, koristim HF API...")
            response = _call_hf_api(messages)
            full_response = response
            # Simuliraj streaming za konzistentnost
            words = response.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield chunk
    
    except Exception as e:
        error_msg = f"\n\n❌ Greška: {str(e)}"
        yield error_msg
        return
    
    # Provjeri ima li tool poziva u odgovoru
    tool_call = parse_tool_call(full_response)
    if tool_call:
        tool_name, tool_args = tool_call
        print(f"[HermesBot] Tool poziv: {tool_name}({tool_args})")
        tool_result = execute_tool(tool_name, tool_args)
        yield f"\n\n**Tool rezultat:**\n{tool_result}"


def chat_sync(
    user_message: str,
    history: list[dict],
    model: Optional[str] = None
) -> str:
    """Sync verzija chat funkcije (za Telegram/Discord)."""
    active_model = model or OLLAMA_MODEL
    system_prompt = build_system_prompt(user_message)
    
    messages = [{"role": "system", "content": system_prompt}]
    messages += history[-MAX_CONTEXT:]
    messages.append({"role": "user", "content": user_message})
    
    try:
        if _ollama_available():
            response = _call_ollama_sync(messages, active_model)
        else:
            response = _call_hf_api(messages)
    except Exception as e:
        return f"❌ Greška: {str(e)}"
    
    # Provjeri tool pozive
    tool_call = parse_tool_call(response)
    if tool_call:
        tool_name, tool_args = tool_call
        tool_result = execute_tool(tool_name, tool_args)
        response += f"\n\n**Tool rezultat:**\n{tool_result}"
    
    return response


# ─── Status ───────────────────────────────────────────────────────────────────

def get_status() -> dict:
    """Vrati status svih servisa."""
    ollama_ok = _ollama_available()
    hf_ok = bool(HF_TOKEN)
    
    models = []
    if ollama_ok:
        try:
            resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
            models = [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass
    
    return {
        "ollama": {"available": ollama_ok, "host": OLLAMA_HOST, "models": models},
        "hf_api": {"available": hf_ok, "model": HF_MODEL},
        "memory": {"enabled": MEMORY_ENABLED, "file": str(MEMORY_FILE)},
        "skills": {"count": len(list_skills()), "dir": str(SKILLS_DIR)},
        "bot_name": BOT_NAME,
    }
