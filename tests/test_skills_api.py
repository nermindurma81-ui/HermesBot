import sys
from pathlib import Path

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
