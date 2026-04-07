# ☤ HermesBot

AI agent web UI pokretan Ollama + HuggingFace GGUF modelima.  
Inspirisan [Hermes Agent](https://github.com/NousResearch/hermes-agent) od NousResearch.

## Features

- 🤗 **HuggingFace GGUF** — `ollama run hf.co/user/repo:quant` direktno iz UI
- 🦙 **Ollama backend** — lokalni LLM runtime, streaming odgovori
- 🧠 **Perzistentna memorija** — MEMORY.md kroz sesije
- ⚙️ **Tool loop** — `remember`, `recall_memory`, `list_skills`, `ollama_status`, `pull_model`
- 📱 **Mobile-first dark UI** — tabovi: Chat, Modeli, Connectors, Memorija
- ✈️ **Telegram / Discord** ready
- 🚂 **Railway deploy** ready

## Brzi start

```bash
# 1. Kloniraj
git clone <ovaj-repo>
cd hermesbot

# 2. Env vars
cp .env.example .env
# Uredi .env

# 3. Pokreni Ollama
ollama serve

# 4. Povuci model sa HuggingFace
ollama run hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M

# 5. Pokreni web app
pip install -r requirements.txt
python app.py
```

## Railway Deploy

### Korak 1 — Push na GitHub
```bash
git init
git add .
git commit -m "HermesBot initial"
git remote add origin https://github.com/TVOJ_USER/hermesbot.git
git push -u origin main
```

### Korak 2 — Railway setup
1. Idi na [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub repo** → odaberi `hermesbot`
3. Dodaj **Ollama servis**:
   - New Service → Docker Image → `ollama/ollama`
   - Dodaj volume `/root/.ollama`
4. Postavi env vars:

```
OLLAMA_HOST=http://ollama.railway.internal:11434
HF_MODEL=bartowski/Llama-3.2-1B-Instruct-GGUF
HF_QUANT=Q4_K_M
BOT_NAME=HermesBot
MEMORY_ENABLED=true
PORT=5000
```

5. Deploy → otvori web URL → idi na **Modeli** tab → Pull model

### Korak 3 — Pull model na Railway Ollama
U Railway konzoli Ollama servisa:
```bash
ollama run hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M
```
Ili kroz web UI → **Modeli** tab → odaberi model → Pull.

## Privatni HF Modeli

```bash
# 1. Kopiraj Ollama SSH key
cat ~/.ollama/id_ed25519.pub

# 2. Dodaj na https://huggingface.co/settings/keys

# 3. Sada možeš koristiti privatne modele:
ollama run hf.co/tvoj-user/privatni-model-GGUF
```

## Env Vars

| Var | Default | Opis |
|-----|---------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama URL |
| `HF_MODEL` | `bartowski/Llama-3.2-1B-Instruct-GGUF` | HF model repo |
| `HF_QUANT` | `Q4_K_M` | Kvantizacija |
| `HF_SPACE_BASE_URL` | — | Opcionalni fallback endpoint (OpenAI-compatible `/v1/chat/completions`) |
| `HF_SPACE_API_KEY` | — | Opcionalni Bearer token za privatni HF Space |
| `HF_SPACE_MODEL` | `default` | Model ime koje se šalje HF Space endpointu |
| `BOT_NAME` | `HermesBot` | Ime bota |
| `SYSTEM_PROMPT` | `You are Hermes...` | System prompt |
| `MEMORY_ENABLED` | `true` | Memorija on/off |
| `MAX_CONTEXT_MESSAGES` | `20` | Max poruka u kontekstu |
| `TELEGRAM_BOT_TOKEN` | — | Telegram integracija |
| `DISCORD_BOT_TOKEN` | — | Discord integracija |
| `PORT` | `5000` | HTTP port |

## Arhitektura

```
hermesbot/
├── app.py              # Flask web server + API rute
├── hermes_core/
│   └── agent.py        # Hermes Agent engine
│       ├── chat_stream()    # Ollama streaming chat
│       ├── execute_tool()   # Tool loop
│       ├── load/save_memory()
│       └── list/save_skill()
├── templates/
│   └── index.html      # Mobile-first dark UI
├── memory/
│   └── MEMORY.md       # Perzistentna memorija (auto)
├── skills/
│   └── *.md            # Skillovi (auto)
├── requirements.txt
├── Procfile
├── railway.json
└── .env.example
```

## Dual backend (Ollama + HF Space fallback)

Ako želiš da radi i druga opcija bez izmjene frontenda:

1. Ostavi postojeći `OLLAMA_HOST`.
2. Dodaj `HF_SPACE_BASE_URL=https://<tvoj-space>.hf.space`
3. Opcionalno: `HF_SPACE_API_KEY=...` i `HF_SPACE_MODEL=...`

Hermes prvo pokušava Ollama; ako Ollama nije dostupan, automatski prelazi na HF Space `/v1/chat/completions`.

### HF Space: brzi postupak + direktni linkovi

Ako na HF Space vidiš `{"detail":"Not Found"}` na `/`, to je normalno ako nisi definisao root rutu. Bitno je da rade `/health` i `/v1/chat/completions`.

1. Kreiraj Docker Space:  
   https://huggingface.co/new-space
2. U browseru kreiraj fajlove (zamijeni `<owner>` i `<space>`):
   - `app.py`: `https://huggingface.co/spaces/<owner>/<space>/new/main?filename=app.py`
   - `requirements.txt`: `https://huggingface.co/spaces/<owner>/<space>/new/main?filename=requirements.txt`
   - `Dockerfile`: `https://huggingface.co/spaces/<owner>/<space>/new/main?filename=Dockerfile`
3. Nakon builda testiraj:
   - Health: `https://<space>.hf.space/health`
   - Chat endpoint: `https://<space>.hf.space/v1/chat/completions`
4. Railway (Hermes app) env:
   - `HF_SPACE_BASE_URL=https://<space>.hf.space`
   - `HF_SPACE_MODEL=default` (opcionalno)
   - `HF_SPACE_API_KEY=...` (samo ako je Space private)

Primjer test poziva:

```bash
curl -X POST "https://<space>.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"default","messages":[{"role":"user","content":"Pozdrav"}]}'
```

### Gotovi fajlovi u ovom repo-u (copy/paste za HF Space)

Ako želiš da ne pišeš ručno, koristi ove fajlove direktno:

- `deploy/hf-space-gateway/app.py`
- `deploy/hf-space-gateway/requirements.txt`
- `deploy/hf-space-gateway/Dockerfile`

Direktni GitHub linkovi:

- <https://github.com/nermindurma81-ui/HermesBot/blob/main/deploy/hf-space-gateway/app.py>
- <https://github.com/nermindurma81-ui/HermesBot/blob/main/deploy/hf-space-gateway/requirements.txt>
- <https://github.com/nermindurma81-ui/HermesBot/blob/main/deploy/hf-space-gateway/Dockerfile>

U ovom template-u je dodata i `GET /` ruta (vrati JSON status), tako da više nećeš dobijati 404 na root putanji.

### Brzi check za tvoj konkretan Space

Ako je Space naziv `nermind/hermes-openai-gateway`, testiraj baš ove URL-ove:

- `https://huggingface.co/spaces/nermind/hermes-openai-gateway` (repo stranica)
- `https://nermind-hermes-openai-gateway.hf.space/` (root)
- `https://nermind-hermes-openai-gateway.hf.space/health`
- `https://nermind-hermes-openai-gateway.hf.space/v1/chat/completions`

Ako root i dalje vraća 404, znači da `app.py` u tom Space-u još nema `@app.get("/")` rutu ili nije deployan najnoviji commit.

## Licenca
MIT
