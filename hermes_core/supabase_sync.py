"""
Supabase Sync — HermesBot
Sinkronizuje: chat historiju, memoriju, skillove
između sesija koristeći Supabase kao backend.

ENV varijable potrebne:
  SUPABASE_URL  = https://xxxx.supabase.co
  SUPABASE_KEY  = your-anon-or-service-key
  SESSION_ID    = optional, default "default"

SQL za kreiranje tabela (pokreni u Supabase SQL Editor):
------------------------------------------------------
CREATE TABLE IF NOT EXISTS hermes_memory (
  id         BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL DEFAULT 'default',
  content    TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hermes_skills (
  id         BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL DEFAULT 'default',
  name       TEXT NOT NULL,
  content    TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(session_id, name)
);

CREATE TABLE IF NOT EXISTS hermes_chat (
  id         BIGSERIAL PRIMARY KEY,
  session_id TEXT NOT NULL DEFAULT 'default',
  role       TEXT NOT NULL,
  content    TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_session   ON hermes_chat(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_skills_session ON hermes_skills(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_session ON hermes_memory(session_id);
------------------------------------------------------
"""

import os
import json
import datetime
import httpx
from pathlib import Path
from typing import Optional

# ── CONFIG ────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SESSION_ID   = os.environ.get("SESSION_ID", "default")

BASE_DIR     = Path(__file__).parent.parent
MEMORY_FILE  = BASE_DIR / "memory" / "MEMORY.md"
SKILLS_DIR   = BASE_DIR / "skills"


def _headers() -> dict:
    return {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }


def _available() -> bool:
    """Check if Supabase is configured."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _url(table: str) -> str:
    return f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table}"


# ── MEMORY SYNC ───────────────────────────────────────────────────

def push_memory() -> bool:
    """Upload local MEMORY.md to Supabase."""
    if not _available():
        return False
    try:
        content = MEMORY_FILE.read_text() if MEMORY_FILE.exists() else ""

        # Upsert — update if exists, insert if not
        resp = httpx.get(
            _url("hermes_memory"),
            headers={**_headers(), "Prefer": ""},
            params={"session_id": f"eq.{SESSION_ID}", "select": "id"},
            timeout=10
        )
        existing = resp.json()

        if existing:
            row_id = existing[0]["id"]
            httpx.patch(
                f"{_url('hermes_memory')}?id=eq.{row_id}",
                headers=_headers(),
                json={"content": content, "updated_at": datetime.datetime.utcnow().isoformat()},
                timeout=10
            )
        else:
            httpx.post(
                _url("hermes_memory"),
                headers=_headers(),
                json={"session_id": SESSION_ID, "content": content},
                timeout=10
            )
        return True
    except Exception as e:
        print(f"[Supabase] push_memory error: {e}")
        return False


def pull_memory() -> bool:
    """Download memory from Supabase to local MEMORY.md."""
    if not _available():
        return False
    try:
        resp = httpx.get(
            _url("hermes_memory"),
            headers={**_headers(), "Prefer": ""},
            params={"session_id": f"eq.{SESSION_ID}", "select": "content"},
            timeout=10
        )
        data = resp.json()
        if data:
            MEMORY_FILE.parent.mkdir(exist_ok=True)
            MEMORY_FILE.write_text(data[0]["content"])
        return True
    except Exception as e:
        print(f"[Supabase] pull_memory error: {e}")
        return False


# ── SKILLS SYNC ───────────────────────────────────────────────────

def push_skills() -> bool:
    """Upload all local skills to Supabase."""
    if not _available():
        return False
    try:
        for f in SKILLS_DIR.glob("*.md"):
            name    = f.stem
            content = f.read_text()
            httpx.post(
                _url("hermes_skills"),
                headers={**_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
                json={
                    "session_id": SESSION_ID,
                    "name":       name,
                    "content":    content,
                    "updated_at": datetime.datetime.utcnow().isoformat()
                },
                timeout=10
            )
        return True
    except Exception as e:
        print(f"[Supabase] push_skills error: {e}")
        return False


def pull_skills() -> bool:
    """Download all skills from Supabase to local skills dir."""
    if not _available():
        return False
    try:
        resp = httpx.get(
            _url("hermes_skills"),
            headers={**_headers(), "Prefer": ""},
            params={"session_id": f"eq.{SESSION_ID}", "select": "name,content"},
            timeout=10
        )
        data = resp.json()
        SKILLS_DIR.mkdir(exist_ok=True)
        for row in data:
            (SKILLS_DIR / f"{row['name']}.md").write_text(row["content"])
        return True
    except Exception as e:
        print(f"[Supabase] pull_skills error: {e}")
        return False


# ── CHAT HISTORY SYNC ─────────────────────────────────────────────

def push_message(role: str, content: str) -> bool:
    """Save a single chat message to Supabase."""
    if not _available():
        return False
    try:
        httpx.post(
            _url("hermes_chat"),
            headers=_headers(),
            json={"session_id": SESSION_ID, "role": role, "content": content},
            timeout=10
        )
        return True
    except Exception as e:
        print(f"[Supabase] push_message error: {e}")
        return False


def pull_chat_history(limit: int = 50) -> list[dict]:
    """Load recent chat history from Supabase."""
    if not _available():
        return []
    try:
        resp = httpx.get(
            _url("hermes_chat"),
            headers={**_headers(), "Prefer": ""},
            params={
                "session_id": f"eq.{SESSION_ID}",
                "select":     "role,content,created_at",
                "order":      "created_at.desc",
                "limit":      str(limit)
            },
            timeout=10
        )
        messages = resp.json()
        # Vrati u hronološkom redu (najstarije prvo)
        return [{"role": m["role"], "content": m["content"]}
                for m in reversed(messages)]
    except Exception as e:
        print(f"[Supabase] pull_chat_history error: {e}")
        return []


def clear_chat_history() -> bool:
    """Delete all chat messages for this session."""
    if not _available():
        return False
    try:
        httpx.delete(
            _url("hermes_chat"),
            headers={**_headers(), "Prefer": ""},
            params={"session_id": f"eq.{SESSION_ID}"},
            timeout=10
        )
        return True
    except Exception as e:
        print(f"[Supabase] clear_chat_history error: {e}")
        return False


# ── FULL SYNC ─────────────────────────────────────────────────────

def sync_on_startup() -> dict:
    """
    Pozovi ovo kada se aplikacija pokrene.
    Preuzima memoriju i skillove sa Supabase.
    """
    if not _available():
        return {"status": "skipped", "reason": "SUPABASE_URL or SUPABASE_KEY not set"}

    results = {
        "memory": pull_memory(),
        "skills": pull_skills(),
    }
    return {"status": "ok", "results": results}


def sync_on_shutdown() -> dict:
    """
    Pozovi ovo prije gašenja ili periodično.
    Šalje lokalnu memoriju i skillove na Supabase.
    """
    if not _available():
        return {"status": "skipped"}

    results = {
        "memory": push_memory(),
        "skills": push_skills(),
    }
    return {"status": "ok", "results": results}


def status() -> str:
    """Vrati status Supabase konekcije."""
    if not _available():
        return "❌ Supabase nije konfigurisan. Dodaj SUPABASE_URL i SUPABASE_KEY u Railway Variables."
    try:
        resp = httpx.get(
            _url("hermes_memory"),
            headers={**_headers(), "Prefer": ""},
            params={"limit": "1"},
            timeout=5
        )
        if resp.status_code == 200:
            return f"✅ Supabase konekcija OK | Session: {SESSION_ID}"
        return f"⚠️ Supabase greška: HTTP {resp.status_code}"
    except Exception as e:
        return f"❌ Supabase nedostupan: {e}"
