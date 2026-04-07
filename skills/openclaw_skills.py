CATALOG = {
    "git_github": ["agent-commons", "agent-team-orchestration", "auto-pr-merger", "azure-devops", "bitbucket-automation"],
    "coding_ides": ["0g-compute", "agent-browser", "agent-self-reflection", "agent-zero", "agentaudit"],
    "browser_automation": ["1p-shortlink", "activecampaign", "agent-browser", "agent-daily-planner", "agent-device"],
    "web_frontend": ["0xwork", "adobe-automator", "aegis-shield", "agent-analytics", "agent-chat", "agentic-security-audit"],
    "devops_cloud": ["account-workflows", "adguard", "aegis-audit", "agent-autonomy-primitives", "agent-directory", "agentic-devops"],
    "image_video": ["ace-music", "adobe-automator", "ai-avatar-generation", "ai-headshot-generation", "ai-video-gen"],
    "apple_apps": ["apple-contacts", "apple-find-my-local", "apple-health-skill", "apple-mail-search", "apple-photos"],
    "search_research": ["academic-deep-research", "academic-writer", "agent-brain", "agent-deep-research", "agentic-paper-digest"],
    "ai_llms": ["4claw", "adaptive-suite", "adversarial-prompting", "agent-autonomy-kit", "agent-memory", "agent-orchestrator"],
    "data_analytics": ["add-analytics", "amplitude-automation", "data-analyst", "data-enricher", "duckdb-en"],
}

LINKS = {
    "clawhub": "https://clawhub.ai/",
    "github": "https://github.com/VoltAgent/awesome-openclaw-skills",
    "openclaw": "https://clawskills.sh/",
    "discord": "https://discord.gg/openclaw",
}


def run(action: str = "list", query: str = "", category: str = ""):
    action = (action or "list").strip().lower()
    query = (query or "").strip().lower()
    category = (category or "").strip().lower()

    if action == "links":
        return "\n".join(f"- {k}: {v}" for k, v in LINKS.items())

    if action == "categories":
        return "Kategorije:\n" + "\n".join(f"- {k}" for k in sorted(CATALOG.keys()))

    if action == "category":
        if not category:
            return "❌ Nedostaje parametar `category`."
        skills = CATALOG.get(category)
        if not skills:
            return f"❌ Nepoznata kategorija: {category}"
        return f"{category}:\n" + "\n".join(f"- {s}" for s in skills)

    if action == "search":
        if not query:
            return "❌ Nedostaje parametar `query`."
        hits = []
        for cat, skills in CATALOG.items():
            for s in skills:
                if query in s.lower():
                    hits.append((cat, s))
        if not hits:
            return f"Nema rezultata za: {query}"
        return "\n".join(f"- {s} ({cat})" for cat, s in hits)

    total = sum(len(v) for v in CATALOG.values())
    lines = [f"OpenClaw katalog (uzorak): {total} skillova u {len(CATALOG)} kategorija"]
    for cat, skills in CATALOG.items():
        lines.append(f"- {cat}: {', '.join(skills)}")
    return "\n".join(lines)
