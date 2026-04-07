#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="${SKILLS_DIR:-skills}"

echo "📚 Installing SKILL.md packs into ${SKILLS_DIR}..."
mkdir -p "${SKILLS_DIR}"

mkdir -p "${SKILLS_DIR}/coding"
cat > "${SKILLS_DIR}/coding/SKILL.md" <<'EOF'
---
name: coding
description: "Use for code writing, debugging and programming implementation tasks"
triggers: ["code", "python", "javascript", "bug", "debug", "script", "function"]
---

# Coding Skill

- Explain plan briefly before code.
- Use fenced code blocks with language tag.
- Mention edge cases when relevant.
EOF

mkdir -p "${SKILLS_DIR}/planning"
cat > "${SKILLS_DIR}/planning/SKILL.md" <<'EOF'
---
name: planning
description: "Use for implementation plans, milestones and step-by-step task breakdown"
triggers: ["plan", "steps", "koraci", "implement", "project"]
---

# Planning Skill

- Provide numbered steps.
- Call out dependencies and priority.
- Keep plan practical and concise.
EOF

mkdir -p "${SKILLS_DIR}/memory"
cat > "${SKILLS_DIR}/memory/SKILL.md" <<'EOF'
---
name: memory
description: "Use when user asks to remember, recall or forget persistent information"
triggers: ["remember", "memory", "zapamti", "sjeti", "zaboravi"]
---

# Memory Skill

- Confirm what was saved.
- Never fabricate recalled memory.
EOF

mkdir -p "${SKILLS_DIR}/bcs_assistant"
cat > "${SKILLS_DIR}/bcs_assistant/SKILL.md" <<'EOF'
---
name: bcs_assistant
description: "Use for Bosnian/Croatian/Serbian language tone and style matching"
triggers: ["sta", "kako", "hvala", "molim", "zdravo", "cao"]
---

# BCS Assistant Skill

- Reply in the same B/H/S variant as user.
- Keep tone natural and direct.
EOF

echo "✅ Installed skills:"
find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md -print | sed 's#^# - #' 
