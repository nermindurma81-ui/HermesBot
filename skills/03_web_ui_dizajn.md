# 🎨 Web Dizajn i UI Dizajn

## OBAVEZNO: Uvijek generiši kompletan HTML/CSS — nikad samo opis

## Dizajn Sistem — Hermes Dark Theme
```css
:root {
  --bg:      #0f0f13;   /* pozadina */
  --surface: #1a1a24;   /* kartice/paneli */
  --surface2:#232333;   /* uzdignuti elementi */
  --border:  #2e2e40;   /* obrubi */
  --accent:  #7c6af7;   /* ljubičasta — primarna */
  --accent2: #5eead4;   /* tirkizna — sekundarna */
  --success: #22c55e;   /* zelena */
  --warning: #f59e0b;   /* žuta */
  --danger:  #ef4444;   /* crvena */
  --text:    #e8e8f0;   /* glavni tekst */
  --muted:   #888899;   /* sekundarni tekst */
  --radius:  12px;
}
```

## Workflow — Web Dizajn Zadatak
1. Razumi šta korisnik treba (landing, dashboard, forma, portfolio...)
2. Odmah generiši kompletan HTML/CSS/JS
3. create_webpage ili write_file
4. Prikaži naziv sačuvanog fajla

## Komponente — Gotovi Recepti

### Hero sekcija
```html
<section style="text-align:center;padding:4rem 2rem;background:linear-gradient(135deg,#1a1a24,#0f0f13)">
  <h1 style="font-size:3rem;color:#7c6af7;margin-bottom:1rem">Naslov</h1>
  <p style="color:#888899;font-size:1.2rem;margin-bottom:2rem">Opis</p>
  <a href="#" style="padding:.875rem 2.5rem;background:#7c6af7;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">Počni →</a>
</section>
```

### Kartica
```html
<div style="background:#1a1a24;border:1px solid #2e2e40;border-radius:12px;padding:1.5rem">
  <h3 style="color:#7c6af7;margin-bottom:.5rem">Naslov</h3>
  <p style="color:#888899">Opis sadržaja kartice.</p>
</div>
```

### Grid layout (responsive)
```html
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem">
  <!-- kartice ovdje -->
</div>
```

### Navbar
```html
<nav style="background:#1a1a24;border-bottom:1px solid #2e2e40;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100">
  <span style="color:#7c6af7;font-weight:700;font-size:1.2rem">Logo</span>
  <div style="display:flex;gap:1.5rem">
    <a href="#" style="color:#e8e8f0;text-decoration:none">Link</a>
  </div>
</nav>
```

### Forma
```html
<form style="display:flex;flex-direction:column;gap:1rem;max-width:400px">
  <label style="color:#888899;font-size:.875rem">Email</label>
  <input type="email" placeholder="email@example.com"
    style="background:#1a1a24;border:1px solid #2e2e40;color:#e8e8f0;padding:.75rem 1rem;border-radius:8px;outline:none">
  <button style="background:#7c6af7;color:#fff;padding:.75rem;border:none;border-radius:8px;cursor:pointer;font-weight:600">
    Pošalji
  </button>
</form>
```

### Badge/Tag
```html
<span style="background:#7c6af720;color:#7c6af7;padding:.25rem .75rem;border-radius:999px;font-size:.8rem;font-weight:600">
  Novo
</span>
```

### Tabela podataka
```html
<table style="width:100%;border-collapse:collapse">
  <thead>
    <tr style="border-bottom:2px solid #2e2e40">
      <th style="color:#7c6af7;padding:.75rem;text-align:left">Kolona</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid #2e2e40">
      <td style="padding:.75rem;color:#e8e8f0">Vrijednost</td>
    </tr>
  </tbody>
</table>
```

### Sidebar layout
```html
<div style="display:grid;grid-template-columns:240px 1fr;min-height:100vh">
  <aside style="background:#1a1a24;border-right:1px solid #2e2e40;padding:1.5rem">
    <!-- sidebar navigacija -->
  </aside>
  <main style="padding:2rem">
    <!-- glavni sadržaj -->
  </main>
</div>
```

## Tipovi stranica — Šta odmah kreirati

| Zahtjev | Akcija |
|---|---|
| Landing page | create_webpage sa hero+features+CTA |
| Portfolio | create_webpage sa grid projektima |
| Dashboard | write_file sa sidebar+kartice+grafovi |
| Blog post | create_webpage sa article layoutom |
| Forma/kalkulator | write_file sa JS logikom |
| Dokumentacija | create_webpage sa sidebar navigacijom |

## Animacije (dodaj u <style>)
```css
@keyframes fadeIn {
  from { opacity:0; transform:translateY(20px); }
  to   { opacity:1; transform:translateY(0); }
}
.animate { animation: fadeIn .5s ease forwards; }

/* Hover efekti */
.card { transition: transform .2s, box-shadow .2s; }
.card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px #7c6af730; }
```

## JavaScript — Interaktivnost
```html
<script>
// Uvijek dodaj u fajl ako treba interaktivnost
// Tema toggle, modal, tabs, accordion...
</script>
```
