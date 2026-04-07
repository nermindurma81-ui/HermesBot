# 🖌️ Grafički Dizajn, Arhitektura i Crtanje

## SVG Generisanje — Uvijek izvrši, ne opisuj

### Kada korisnik traži dijagram/crtež → generiši SVG i sačuvaj

## SVG — Osnove
```svg
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <!-- pozadina -->
  <rect width="800" height="600" fill="#0f0f13"/>
  
  <!-- tekst -->
  <text x="400" y="50" text-anchor="middle" fill="#7c6af7" 
        font-family="Arial" font-size="24" font-weight="bold">
    Naslov Dijagrama
  </text>
  
  <!-- kutija -->
  <rect x="50" y="100" width="200" height="80" rx="8"
        fill="#1a1a24" stroke="#7c6af7" stroke-width="2"/>
  <text x="150" y="145" text-anchor="middle" fill="#e8e8f0" font-size="14">
    Komponenta
  </text>
  
  <!-- strelica -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#7c6af7"/>
    </marker>
  </defs>
  <line x1="250" y1="140" x2="350" y2="140" stroke="#7c6af7" 
        stroke-width="2" marker-end="url(#arrow)"/>
</svg>
```

## Tipovi dijagrama — Šta generisati

### Flowchart (tok procesa)
```
Korisnik: "napravi flowchart za login"
→ SVG sa: Start → Unesi podatke → Provjeri → [Da] Pristup / [Ne] Greška
```

### Arhitekturni dijagram
```
Korisnik: "nacrtaj arhitekturu app-a"
→ SVG: Frontend → API → Database, sa strelicama i labelama
```

### Wireframe
```
Korisnik: "wireframe za dashboard"
→ SVG: Navbar, Sidebar, Main area, Cards — sve kao pravougaonici sa labelama
```

### Organizacioni dijagram
```
→ SVG stabla sa čvorovima i vezama
```

## Arhitekturno Znanje

### Web App Arhitektura
```
Frontend (React/Vue/HTML)
    ↓ HTTP/REST/GraphQL
Backend (FastAPI/Flask/Express)
    ↓ ORM/Query
Database (PostgreSQL/MongoDB/Supabase)
    ↓ 
Cache (Redis) | Storage (S3/R2) | Queue (RabbitMQ)
```

### Mikroservisi
```
API Gateway → Auth Service
           → User Service  
           → Payment Service
           → Notification Service
Svaki servis ima vlastiti DB
```

### Deployment arhitektura
```
GitHub → CI/CD (GitHub Actions)
       → Docker Build
       → Railway/Vercel/Fly.io
       → CDN (Cloudflare)
```

## Građevinsko Znanje

### Osnove konstruktivnog projektovanja
- **Nosivi zidovi** — prenose opterećenje na temelje
- **Armirani beton** — beton + čelik za savijanje/pritisak
- **Temelji** — trake, ploče, piloti (ovisno o tlu)
- **Statički sistemi** — greda, luk, okvir, ploča

### Dimenzionisanje (orijentaciono)
```
Greda: visina ≈ raspon/12 do raspon/10
Stup:  min 25x25cm za stambene objekte
Ploča: debljina ≈ raspon/30 (jednosmjerna)
Temeljna traka: širina ≈ 2x debljina zida
```

### Materijali
| Materijal | Primjena | Prednosti |
|---|---|---|
| Armirani beton | Skeletne konstrukcije | Čvrstoća, trajnost |
| Čelik | Industrijski objekti, mostovi | Lagano, fleksibilno |
| Drvo | Stambeni objekti, krovovi | Ekološko, brzina gradnje |
| Opeka | Zidovi, fasade | Izolacija, estetika |

### Crtanje nacrta — SVG Primjer
```svg
<!-- Tlocrt sobe -->
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#0f0f13"/>
  <!-- Zidovi (debele linije) -->
  <rect x="50" y="50" width="300" height="200" 
        fill="none" stroke="#e8e8f0" stroke-width="8"/>
  <!-- Vrata (luk) -->
  <line x1="50" y1="150" x2="50" y2="200" stroke="#0f0f13" stroke-width="8"/>
  <path d="M 50 150 Q 90 150 90 190" fill="none" stroke="#7c6af7" stroke-width="2"/>
  <!-- Prozor -->
  <line x1="200" y1="50" x2="280" y2="50" stroke="#5eead4" stroke-width="8"/>
  <!-- Dimenzije -->
  <text x="200" y="270" text-anchor="middle" fill="#888899" font-size="12">5.00m</text>
</svg>
```

## Grafički Dizajn Principi

### Tipografija
- **Heading**: bold, veće, kontrastna boja
- **Body**: regular, 16px min, dobar line-height (1.5-1.7)
- **Caption**: muted boja, manje

### Razmaci (8px grid sistem)
```
4px  → micro (ikone, tagovi)
8px  → mali (padding teksta)
16px → srednji (između elemenata)
24px → veći (sekcije)
32px → veliki (razmak sekcija)
64px → hero razmaci
```

### Boje — Pravilo 60-30-10
- 60% neutralna (pozadina)
- 30% surface (kartice, paneli)
- 10% accent (CTA, linkovi, highlight)

### Logo generisanje (SVG tekst+oblici)
```svg
<svg viewBox="0 0 200 60">
  <rect x="0" y="10" width="40" height="40" rx="8" fill="#7c6af7"/>
  <text x="14" y="36" fill="#fff" font-size="20" font-weight="bold">H</text>
  <text x="50" y="36" fill="#e8e8f0" font-size="22" font-weight="700">Hermes</text>
</svg>
```
