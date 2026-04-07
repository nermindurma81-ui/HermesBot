import sys
from pathlib import Path
import subprocess
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, _detect_public_base_url
from orchestrator import HermesOrchestrator
import hermes_core.agent as agent_module
from skills import web_search as web_search_skill


def test_skills_market_and_python_listing():
    client = app.test_client()

    market = client.get("/api/skills/market")
    assert market.status_code == 200
    payload = market.get_json()
    assert payload["market"]
    assert "github" in payload["links"]

    py_skills = client.get("/api/skills/python")
    assert py_skills.status_code == 200
    skills = py_skills.get_json()["skills"]
    assert "weather" in skills


def test_skill_get_supports_python_files():
    client = app.test_client()

    response = client.get("/api/skills/weather")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["type"] in ("python", "markdown")
    assert "run(" in payload["content"]


def test_explicit_skill_command_format():
    orchestrator = HermesOrchestrator()
    tool, output = orchestrator.detect_intent_and_execute('/skill hello name="Nermin"')
    assert tool == "hello"
    assert "Nermin" in output


def test_connectors_status_endpoints_without_tokens():
    client = app.test_client()
    tg = client.get("/api/connectors/telegram/status")
    gh = client.get("/api/connectors/github/status")
    assert tg.status_code == 200
    assert gh.status_code == 200
    assert tg.get_json()["status"] == "missing_token"
    assert gh.get_json()["status"] == "missing_token"

    tg_set = client.post("/api/connectors/telegram/webhook/set", json={})
    assert tg_set.status_code == 400
    assert tg_set.get_json()["status"] == "missing_token"


def test_skill_command_requires_params():
    orchestrator = HermesOrchestrator()
    tool, output = orchestrator.detect_intent_and_execute('/skill web_search')
    assert tool == "skill_error"
    assert "Nedostaju parametri" in output


def test_auto_router_prefers_web_search_for_lookup_queries():
    orchestrator = HermesOrchestrator()
    tool, output = orchestrator.detect_intent_and_execute("Nadji cijenu passata 1.9 tdi")
    assert tool == "web_search"
    assert isinstance(output, str)


def test_chat_direct_skill_stream_includes_content_chunk():
    client = app.test_client()
    resp = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Nadji informacije o Python programming language"}]})
    body = resp.data.decode("utf-8")
    assert '"tool_call": "web_search"' in body
    assert '"content":' in body


def test_ollama_status_reports_offline_for_unreachable_host(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:65530")
    client = app.test_client()
    data = client.get("/api/ollama/status").get_json()
    assert data["online"] is False


def test_deep_sanity_script():
    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "deep_sanity_check.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "DEEP_SANITY_OK" in proc.stdout


def test_telegram_webhook_ignored_without_text(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x:dummy")
    client = app.test_client()
    r = client.post("/api/telegram/webhook", json={"message": {"chat": {"id": 1}}})
    assert r.status_code == 200
    assert r.get_json()["ignored"] is True


def test_detect_public_base_url_prefers_railway_domain(monkeypatch):
    monkeypatch.delenv("TELEGRAM_WEBHOOK_BASE_URL", raising=False)
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.delenv("RAILWAY_STATIC_URL", raising=False)
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "my-hermes.up.railway.app")
    with app.test_request_context("/", base_url="http://localhost:5000"):
        assert _detect_public_base_url() == "https://my-hermes.up.railway.app"


def test_detect_public_base_url_payload_has_priority(monkeypatch):
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "my-hermes.up.railway.app")
    with app.test_request_context("/", base_url="https://internal.local"):
        assert _detect_public_base_url("https://custom.example.com") == "https://custom.example.com"


def test_telegram_status_reports_expected_webhook(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x:dummy")
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "my-hermes.up.railway.app")

    class _Resp:
        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

    def fake_get(url, timeout=10):
        if url.endswith("/getMe"):
            return _Resp({"ok": True, "result": {"username": "MojHermesBot"}})
        return _Resp({"ok": True, "result": {"url": "https://my-hermes.up.railway.app/api/telegram/webhook"}})

    monkeypatch.setitem(sys.modules, "httpx", types.SimpleNamespace(get=fake_get))
    client = app.test_client()
    data = client.get("/api/connectors/telegram/status").get_json()
    assert data["ok"] is True
    assert data["webhook_ok"] is True
    assert data["expected_webhook_url"] == "https://my-hermes.up.railway.app/api/telegram/webhook"


def test_skill_save_python_and_reject_invalid_python():
    client = app.test_client()

    bad = client.post("/api/skills/tmp_exec_skill", json={"type": "python", "content": "print('x')"})
    assert bad.status_code == 400
    assert "must include def run" in bad.get_json()["error"]

    good = client.post(
        "/api/skills/tmp_exec_skill",
        json={"type": "python", "content": "def run(query=''):\n    return query or 'ok'\n"}
    )
    assert good.status_code == 200
    payload = good.get_json()
    assert payload["ok"] is True
    assert payload["type"] == "python"

    loaded = client.get("/api/skills/tmp_exec_skill")
    assert loaded.status_code == 200
    assert loaded.get_json()["type"] == "python"

    client.delete("/api/skills/tmp_exec_skill")


def test_chat_stream_falls_back_to_hf_space(monkeypatch):
    cfg = agent_module.get_cfg()
    cfg["ollama_host"] = "http://127.0.0.1:65531"
    cfg["hf_space_base_url"] = "https://example-space.hf.space"
    cfg["hf_space_model"] = "test-model"
    cfg["hf_space_api_key"] = ""

    class _FakeStreamCtx:
        def __enter__(self):
            raise agent_module.httpx.ConnectError("offline")

        def __exit__(self, exc_type, exc, tb):
            return False

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def stream(self, *args, **kwargs):
            return _FakeStreamCtx()

    class _Resp:
        status_code = 200

        @staticmethod
        def json():
            return {"choices": [{"message": {"content": "HF fallback radi"}}]}

    monkeypatch.setattr(agent_module.httpx, "Client", _FakeClient)
    monkeypatch.setattr(agent_module.httpx, "post", lambda *a, **k: _Resp())

    chunks = list(agent_module.chat_stream([{"role": "user", "content": "test"}], cfg))
    text = "".join(chunks)
    assert "HF fallback radi" in text
    assert '"done": true' in text.lower()


def test_web_search_handles_wikipedia_403_without_crash(monkeypatch):
    class _Resp:
        def __init__(self, payload=None, status_code=200):
            self._payload = payload or {}
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                req = agent_module.httpx.Request("GET", "https://en.wikipedia.org/w/api.php")
                resp = agent_module.httpx.Response(self.status_code, request=req)
                raise agent_module.httpx.HTTPStatusError("forbidden", request=req, response=resp)

        def json(self):
            return self._payload

    def fake_get(url, params=None, headers=None, timeout=20):
        if "duckduckgo" in url:
            return _Resp(payload={"AbstractText": "", "RelatedTopics": []}, status_code=200)
        return _Resp(payload={}, status_code=403)

    monkeypatch.setattr(web_search_skill.httpx, "get", fake_get)
    out = web_search_skill.run("/install skill web_search")
    assert "Nisam našao rezultate" in out
    assert "install skill web_search" in out


def test_web_search_normalizes_leading_slash():
    assert web_search_skill._normalize_query("/hello world") == "hello world"
