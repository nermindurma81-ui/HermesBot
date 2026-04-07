# 💻 Vibe Coding — Programiranje po Osjećaju

## Šta je Vibe Coding
Brzo pretvaranje ideje u funkcionalan kod bez previše planiranja.
Korisnik kaže šta želi → Hermes odmah piše i izvršava kod.

## OBAVEZNO: Uvijek izvrši kod, ne samo prikaži

### Workflow za svaki coding zadatak
1. Razumi ideju (1 rečenica opisa je dovoljno)
2. Napiši kompletan kod
3. run_python → testiraj
4. Popravi greške automatski
5. write_file → sačuvaj
6. Prikaži rezultat korisniku

## Jezici i tehnologije

### Python
```python
# Uvijek piši runnable kod
# Uključi sve importove
# Testiraj sa run_python
```

### JavaScript/Node
```javascript
// Napiši pa sačuvaj kao .js fajl
// write_file("skripta.js", kod)
```

### Bash skripte
```bash
#!/bin/bash
# Automatiziraj sistemske zadatke
```

## Vibe Coding principi

### "Samo radi" princip
- Ne pitaj za arhitekturu → odmah kodi
- Napravi MVP koji radi → pa poboljšaj
- Greška = fix odmah u sledećoj iteraciji

### Iterativni pristup
```
v1: Radi osnovna funkcija
v2: Dodaj error handling
v3: Optimizuj i refaktoriši
v4: Dodaj UI/API
```

### Tipični vibe coding zadaci
- "Napravi mi skriptu koja..." → run_python odmah
- "Automatiziraj ovo..." → napiši i testiraj
- "Parsuj ovaj JSON..." → run_python sa primjerom
- "Napravi API endpoint..." → napiši Flask/FastAPI kod
- "Scrape ovaj sajt..." → fetch_url + run_python

## Česti Paterni

### Data processing
```python
import json, csv
data = [...]
# Obrada → rezultat → print
```

### Web scraping
```python
# fetch_url za HTML
# re ili BeautifulSoup za parsiranje
# json.dumps za rezultat
```

### API integracija
```python
import httpx
resp = httpx.get("https://api.example.com/data")
print(resp.json())
```

### File obrada
```python
from pathlib import Path
content = Path("fajl.txt").read_text()
# Obrada...
```

## Greške — Automatski fix
Kada run_python vrati grešku:
1. Pročitaj stderr
2. Identificiraj problem
3. Popravi kod
4. run_python ponovo
5. Ponavljaj dok ne radi

## Sačuvaj sve što je korisno
```
write_file("naziv_skripte.py", kod)
write_file("rezultati.json", output)
```
