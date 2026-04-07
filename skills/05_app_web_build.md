# 🚀 App i Web Build — Kompletno Znanje

## OBAVEZNO: Za svaki build zadatak — napiši kod i sačuvaj fajlove

## Web Frontendi

### Vanilla HTML/CSS/JS (uvijek radi odmah)
```
→ create_webpage ili write_file
→ Kompletan, self-contained HTML fajl
→ Bez dependencija = odmah se otvori u browseru
```

### React
```jsx
// Struktura projekta
src/
  components/
    Button.jsx
    Card.jsx
  pages/
    Home.jsx
  App.jsx
  main.jsx

// Komponenta pattern
export default function Button({ children, onClick, variant="primary" }) {
  const styles = {
    primary: "bg-purple-600 text-white px-4 py-2 rounded-lg",
    ghost:   "border border-purple-600 text-purple-400 px-4 py-2 rounded-lg"
  }
  return <button className={styles[variant]} onClick={onClick}>{children}</button>
}
```

### Next.js
```
app/
  page.jsx          → homepage
  layout.jsx        → root layout
  api/route.js      → API endpoint
  [slug]/page.jsx   → dinamične rute
```

### Vue 3
```vue
<script setup>
import { ref, computed } from 'vue'
const count = ref(0)
</script>
<template>
  <button @click="count++">{{ count }}</button>
</template>
```

## Backend

### FastAPI (Python) — Preferirani
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], 
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(body: dict):
    return {"response": "..."}
```

### Flask
```python
from flask import Flask, request, jsonify, Response
app = Flask(__name__)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### Express (Node.js)
```javascript
const express = require('express')
const app = express()
app.use(express.json())

app.get('/api', (req, res) => res.json({ ok: true }))
app.listen(3000)
```

## Baze Podataka

### Supabase (PostgreSQL)
```python
from supabase import create_client
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# Insert
sb.table("users").insert({"name": "Alen"}).execute()

# Select
result = sb.table("users").select("*").eq("id", 1).execute()

# Update
sb.table("users").update({"name": "Novi"}).eq("id", 1).execute()
```

### SQLite (lokalno)
```python
import sqlite3
conn = sqlite3.connect("baza.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO items (name) VALUES (?)", ("Test",))
conn.commit()
```

### MongoDB
```python
from pymongo import MongoClient
client = MongoClient(MONGO_URI)
db = client["hermesdb"]
db.users.insert_one({"name": "Alen", "role": "admin"})
```

## Mobile Apps

### React Native
```
expo init MyApp
→ App.jsx sa React komponentama
→ StyleSheet umjesto CSS
→ Isti JavaScript/TypeScript
```

### Flutter (Dart)
```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Hermes')),
        body: Center(child: Text('Hello!')),
      ),
    );
  }
}
```

## Deployment

### Railway (trenutni hosting)
```
1. Poveži GitHub repo
2. Dodaj varijable okoline
3. Automatski deploy na push
```

### Vercel (frontend)
```bash
vercel --prod
# ili: GitHub Actions → vercel deploy
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: hermesdb
```

## Arhitekturni Paterni

### REST API struktura
```
GET    /api/users          → lista korisnika
POST   /api/users          → novi korisnik
GET    /api/users/{id}     → jedan korisnik
PUT    /api/users/{id}     → ažuriraj
DELETE /api/users/{id}     → briši
```

### Authentication flow
```
1. POST /auth/login → JWT token
2. Header: Authorization: Bearer {token}
3. Backend verifikuje token
4. Refresh token za produžavanje sesije
```

### WebSocket (real-time)
```python
from fastapi import WebSocket
@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"Echo: {data}")
```

## Performance

### Frontend
- Lazy loading slika
- Code splitting (React.lazy)
- Minifikacija CSS/JS
- CDN za statičke fajlove

### Backend
- Async endpoints (FastAPI)
- Connection pooling (baza)
- Redis cache za česte upite
- Pagination (nikad ne vraćaj sve odjednom)
