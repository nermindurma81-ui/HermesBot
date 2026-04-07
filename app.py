import os
import json
import asyncio
import threading
import re  # Za prepoznavanje [skill](params)
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from hermes_core.agent import (
    get_cfg, model_tag, chat_stream,
    ollama_list_models, ollama_pull_stream, ollama_delete_model,
    load_memory, save_memory, list_skills, save_skill, get_skill,
    append_memory, MEMORY_FILE, SKILLS_DIR
)
# IMPORT: Tvoj novi Orchestrator koji pokreće .py skillove
from orchestrator import HermesOrchestrator

# ── SUPABASE (optional) ───────────────────────────────────────────
try:
    from hermes_core import supabase_sync as _sb
    _startup = _sb.sync_on_startup()
    print(f"[Supabase] Startup sync: {_startup}")
    _SUPABASE = True
except Exception as _e:
    _SUPABASE = False
    print(f"[Supabase] Not configured or error: {_e}")

app = Flask(__name__)
UPLOADS_DIR = SKILLS_DIR.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
# Inicijalizacija izvršitelja skillova
orchestrator = HermesOrchestrator()


def _safe_skill_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", (name or "").strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower()


def _market_catalog():
    return {
        "market": "OpenClaw Community (curated sample)",
        "links": {
            "clawhub": "https://clawhub.ai/",
            "github": "https://github.com/VoltAgent/awesome-openclaw-skills",
            "openclaw": "https://clawskills.sh/"
        },
        "install_note": "Za instalaciju pošalji raw .py URL kroz POST /api/skills/market/install",
        "examples": [
            "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/skills/my_skill.py"
        ]
    }


def _extract_file_preview(path, ext: str) -> str:
    ext = (ext or "").lower()
    if ext in {".txt", ".md", ".json", ".csv", ".py", ".log"}:
        return path.read_text(encoding="utf-8", errors="ignore")[:4000]

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            text = "\n".join((p.extract_text() or "") for p in reader.pages[:5])
            return text[:4000]
        except Exception:
            return ""

    if ext == ".docx":
        try:
            import docx  # python-docx
            d = docx.Document(str(path))
            text = "\n".join(p.text for p in d.paragraphs)
            return text[:4000]
        except Exception:
            return ""

    if ext == ".xlsx":
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
            lines = []
            for ws in wb.worksheets[:2]:
                lines.append(f"[Sheet] {ws.title}")
                for row in ws.iter_rows(min_row=1, max_row=20, values_only=True):
                    vals = [str(v) for v in row if v is not None and str(v).strip()]
                    if vals:
                        lines.append(" | ".join(vals))
            return "\n".join(lines)[:4000]
        except Exception:
            return ""

    return ""

# ─────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat/upload", methods=["POST"])
def api_chat_upload():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "Missing file field"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "Empty filename"}), 400

    safe_name = _safe_skill_name(os.path.splitext(f.filename)[0]) or "upload"
    ext = os.path.splitext(f.filename)[1][:12]
    target = UPLOADS_DIR / f"{safe_name}{ext}"
    f.save(target)

    size = target.stat().st_size
    preview = _extract_file_preview(target, ext)

    return jsonify({
        "ok": True,
        "filename": target.name,
        "size": size,
        "preview": preview
    })


@app.route("/api/connectors/telegram/status", methods=["GET"])
def api_telegram_status():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return jsonify({"ok": False, "status": "missing_token"})
    try:
        import httpx
        me = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        webhook = httpx.get(f"https://api.telegram.org/bot{token}/getWebhookInfo", timeout=10).json()
        return jsonify({"ok": bool(me.get("ok")), "me": me.get("result"), "webhook": webhook.get("result")})
    except Exception as e:
        return jsonify({"ok": False, "status": "error", "error": str(e)}), 400


@app.route("/api/connectors/github/status", methods=["GET"])
def api_github_status():
    token = (request.headers.get("Authorization", "").replace("Bearer ", "").strip()
             or os.environ.get("GITHUB_TOKEN", "").strip())
    if not token:
        return jsonify({"ok": False, "status": "missing_token"})
    try:
        import httpx
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        user = httpx.get("https://api.github.com/user", headers=headers, timeout=10)
        repos = httpx.get("https://api.github.com/user/repos?per_page=30&sort=updated", headers=headers, timeout=10)
        if user.status_code != 200:
            return jsonify({"ok": False, "status": "auth_failed", "code": user.status_code, "body": user.text[:300]}), 400
        repos_data = repos.json() if repos.status_code == 200 else []
        return jsonify({
            "ok": True,
            "user": user.json().get("login"),
            "repo_count": len(repos_data),
            "repos": [r.get("full_name") for r in repos_data[:20]]
        })
    except Exception as e:
        return jsonify({"ok": False, "status": "error", "error": str(e)}), 400

# ─────────────────────────────────────────────────────────────────
# CONFIG API
# ─────────────────────────────────────────────────────────────────
@app.route("/api/config")
def api_config():
    cfg = get_cfg()
    safe = {}
    for k, v in cfg.items():
        if k.endswith(("_token", "_key")) and v:
            safe[k] = "***set***"
        else:
            safe[k] = v
    safe["model_tag"] = model_tag(cfg)
    return jsonify(safe)

# ─────────────────────────────────────────────────────────────────
# CHAT API (streaming SSE) - SA SISTEM PROMPTOM I SKILLOVIMA
# ─────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    messages = data.get("messages", [])
    cfg = get_cfg()
    last_user_msg = messages[-1]["content"] if messages else ""

    # 0. Hard skill-first ruta za jasne upite (npr. "koristi skillove", "vrijeme u X")
    direct_skill = orchestrator.detect_intent_and_execute(last_user_msg)
    if direct_skill:
        tool_name, tool_output = direct_skill

        def direct_generate():
            yield f"data: {json.dumps({'tool_call': tool_name, 'args': {'input': last_user_msg}, 'done': False})}\n\n"
            yield f"data: {json.dumps({'tool_result': tool_output, 'tool': tool_name, 'done': False})}\n\n"
            yield f"data: {json.dumps({'content': str(tool_output), 'done': False})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        return Response(
            stream_with_context(direct_generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    # 1. Učitavanje System Prompta (Kataloga)
    system_prompt_path = "system_prompt.txt"
    system_content = ""
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_content = f.read()

    # 2. Priprema poruka za AI (ubacujemo prompt na početak)
    if system_content:
        full_messages = [{"role": "system", "content": system_content}] + messages
    else:
        full_messages = messages

    def generate():
        # 3. Streaming odgovora od AI modela + skupljanje finalnog AI teksta
        full_assistant_content = ""
        saw_done_event = False
        for chunk in chat_stream(full_messages, cfg):
            try:
                if chunk.startswith("data: "):
                    payload = json.loads(chunk[6:].strip())
                    if payload.get("content"):
                        full_assistant_content += payload["content"]
                    # Odgodi finalni "done" dok ne pokušamo izvršiti skill
                    if payload.get("done") is True:
                        saw_done_event = True
                        continue
            except Exception:
                # Ne prekidaj stream ako neki SSE red nije parsabilan
                pass
            yield chunk

        # 4. Provjera je li AI vratio [skill](...) obrazac i izvršavanje Python skilla
        skill_result = orchestrator.parse_response(full_assistant_content)
        if skill_result:
            yield f"data: {json.dumps({'tool_result': skill_result, 'tool': 'skill_orchestrator', 'done': False})}\n\n"
        if saw_done_event:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

# ─────────────────────────────────────────────────────────────────
# OLLAMA / MODELS API
# ─────────────────────────────────────────────────────────────────
@app.route("/api/models")
def api_models():
    cfg = get_cfg()
    models = ollama_list_models(cfg["ollama_host"])
    return jsonify({"models": models, "current": model_tag(cfg)})

@app.route("/api/models/pull", methods=["POST"])
def api_pull():
    data = request.json or {}
    model = data.get("model", "")
    cfg = get_cfg()
    if not model:
        model = model_tag(cfg)

    def generate():
        yield from ollama_pull_stream(model, cfg["ollama_host"])

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@app.route("/api/models/delete", methods=["POST"])
def api_delete_model():
    data = request.json or {}
    model = data.get("model", "")
    cfg = get_cfg()
    result = ollama_delete_model(model, cfg["ollama_host"])
    return jsonify(result)

@app.route("/api/ollama/status")
def api_ollama_status():
    cfg = get_cfg()
    models = ollama_list_models(cfg["ollama_host"])
    return jsonify({
        "online": len(models) >= 0,
        "host": cfg["ollama_host"],
        "model_count": len(models),
        "current_model": model_tag(cfg)
    })

@app.route("/api/hf/popular")
def api_hf_popular():
    popular = [
        {"id": "bartowski/Llama-3.2-1B-Instruct-GGUF",   "quants": ["Q4_K_M","Q8_0","IQ3_M"], "size": "1B",  "desc": "Fast, lightweight"},
        {"id": "bartowski/Llama-3.2-3B-Instruct-GGUF",   "quants": ["Q4_K_M","Q8_0","IQ3_M"], "size": "3B",  "desc": "Balanced speed/quality"},
        {"id": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF", "quants": ["Q4_K_M","Q5_K_M","Q8_0"], "size": "8B", "desc": "High quality"},
        {"id": "bartowski/Mistral-7B-Instruct-v0.3-GGUF","quants": ["Q4_K_M","Q5_K_M","Q8_0"], "size": "7B",  "desc": "Mistral v0.3"},
        {"id": "bartowski/gemma-2-2b-it-GGUF",            "quants": ["Q4_K_M","Q8_0"],           "size": "2B",  "desc": "Google Gemma 2"},
        {"id": "bartowski/Phi-3.5-mini-instruct-GGUF",   "quants": ["Q4_K_M","Q8_0"],           "size": "3.8B","desc": "Microsoft Phi-3.5"},
        {"id": "mlabonne/Meta-Llama-3.1-8B-Instruct-abliterated-GGUF", "quants": ["Q4_K_M","Q8_0"], "size": "8B", "desc": "Uncensored Llama"},
        {"id": "arcee-ai/SuperNova-Medius-GGUF",          "quants": ["Q4_K_M","Q8_0"],           "size": "14B", "desc": "SuperNova Medius"},
        {"id": "bartowski/Qwen2.5-7B-Instruct-GGUF",     "quants": ["Q4_K_M","Q5_K_M","Q8_0"], "size": "7B",  "desc": "Qwen 2.5"},
        {"id": "bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF","quants":["Q4_K_M","Q8_0"],         "size": "7B",  "desc": "DeepSeek R1 Distill"},
    ]
    return jsonify(popular)

# ─────────────────────────────────────────────────────────────────
# MEMORY API
# ─────────────────────────────────────────────────────────────────
@app.route("/api/memory", methods=["GET"])
def api_memory_get():
    return jsonify({"memory": load_memory()})

@app.route("/api/memory", methods=["POST"])
def api_memory_post():
    data = request.json or {}
    content = data.get("content", "")
    save_memory(content)
    return jsonify({"ok": True})

@app.route("/api/memory/append", methods=["POST"])
def api_memory_append():
    data = request.json or {}
    note = data.get("note", "")
    append_memory(note)
    return jsonify({"ok": True})

@app.route("/api/memory/clear", methods=["POST"])
def api_memory_clear():
    save_memory("")
    return jsonify({"ok": True})

# ─────────────────────────────────────────────────────────────────
# SKILLS API (MD & PY)
# ─────────────────────────────────────────────────────────────────
@app.route("/api/skills", methods=["GET"])
def api_skills_list():
    return jsonify(list_skills())


@app.route("/api/skills/python", methods=["GET"])
def api_python_skills_list():
    return jsonify({"skills": orchestrator.list_python_skills()})

@app.route("/api/skills/<name>", methods=["GET"])
def api_skill_get(name):
    md_content = get_skill(name)
    if md_content is not None:
        return jsonify({"name": name, "content": md_content, "type": "markdown"})

    py_path = SKILLS_DIR / f"{name}.py"
    if py_path.exists():
        return jsonify({
            "name": name,
            "content": py_path.read_text(encoding="utf-8"),
            "type": "python"
        })

    return jsonify({"error": "Not found"}), 404

@app.route("/api/skills/<name>", methods=["POST", "PUT"])
def api_skill_save(name):
    data = request.json or {}
    content = data.get("content", "")
    save_skill(name, content)
    return jsonify({"ok": True})

@app.route("/api/skills/<name>", methods=["DELETE"])
def api_skill_delete(name):
    removed = []
    md_path = SKILLS_DIR / f"{name}.md"
    py_path = SKILLS_DIR / f"{name}.py"

    if md_path.exists():
        md_path.unlink()
        removed.append(str(md_path.name))
    if py_path.exists():
        py_path.unlink()
        removed.append(str(py_path.name))

    if removed:
        return jsonify({"ok": True, "removed": removed})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/skills/market", methods=["GET"])
def api_skills_market():
    return jsonify(_market_catalog())


@app.route("/api/skills/market/install", methods=["POST"])
def api_skills_market_install():
    data = request.json or {}
    url = (data.get("url") or "").strip()
    skill_name = _safe_skill_name(data.get("name") or "")

    if not url:
        return jsonify({"ok": False, "error": "Missing 'url'"}), 400

    parsed = urlparse(url)
    if parsed.scheme != "https":
        return jsonify({"ok": False, "error": "Only https URLs are allowed"}), 400
    if not parsed.path.endswith(".py"):
        return jsonify({"ok": False, "error": "URL must point to a .py file"}), 400

    try:
        import httpx
        resp = httpx.get(url, timeout=20)
        resp.raise_for_status()
        code = resp.text
    except Exception as e:
        return jsonify({"ok": False, "error": f"Download failed: {e}"}), 400

    if len(code) > 250_000:
        return jsonify({"ok": False, "error": "Skill file too large"}), 400
    if "def run(" not in code:
        return jsonify({"ok": False, "error": "Skill must expose run(...) function"}), 400

    if not skill_name:
        skill_name = _safe_skill_name(os.path.basename(parsed.path).replace(".py", ""))
    if not skill_name:
        return jsonify({"ok": False, "error": "Cannot derive valid skill name"}), 400

    path = SKILLS_DIR / f"{skill_name}.py"
    path.write_text(code, encoding="utf-8")

    return jsonify({
        "ok": True,
        "name": skill_name,
        "path": str(path),
        "message": f"Skill '{skill_name}' installed"
    })

# ─────────────────────────────────────────────────────────────────
# SUPABASE API
# ─────────────────────────────────────────────────────────────────
@app.route("/api/supabase/status")
def api_supabase_status():
    if not _SUPABASE:
        return jsonify({"status": "disabled", "message": "SUPABASE_URL or SUPABASE_KEY not set"})
    return jsonify({"status": "ok", "message": _sb.status()})

@app.route("/api/supabase/sync", methods=["POST"])
def api_supabase_sync():
    if not _SUPABASE:
        return jsonify({"ok": False, "error": "Supabase not configured"})
    data = request.json or {}
    direction = data.get("direction", "push")
    if direction == "pull":
        result = _sb.sync_on_startup()
    else:
        result = _sb.sync_on_shutdown()
    return jsonify({"ok": True, "result": result})

@app.route("/api/supabase/chat", methods=["GET"])
def api_supabase_chat_history():
    if not _SUPABASE:
        return jsonify({"messages": [], "error": "Supabase not configured"})
    limit = int(request.args.get("limit", 50))
    messages = _sb.pull_chat_history(limit)
    return jsonify({"messages": messages})

@app.route("/api/supabase/chat/clear", methods=["POST"])
def api_supabase_chat_clear():
    if not _SUPABASE:
        return jsonify({"ok": False, "error": "Supabase not configured"})
    ok = _sb.clear_chat_history()
    return jsonify({"ok": ok})

# ─────────────────────────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "hermesbot",
        "supabase": "connected" if _SUPABASE else "disabled"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    finally:
        if _SUPABASE:
            print("[Supabase] Shutdown sync...")
            _sb.sync_on_shutdown()
