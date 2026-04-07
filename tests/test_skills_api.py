import sys
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from orchestrator import HermesOrchestrator


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
